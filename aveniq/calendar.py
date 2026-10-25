"""iCalendar subset for single VEVENT import/export, and read-only CalDAV adapter.
Complex timezone definitions and recurring exceptions are intentionally not flattened.
"""
from __future__ import annotations
import base64, os, ssl, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from .security import InputError


def unfold(raw):
    return raw.replace('\r\n ','').replace('\r\n\t','').replace('\n ','').replace('\n\t','').replace('\r\n','\n')

def ics_unescape(s):return s.replace('\\n','\n').replace('\\,',',').replace('\\;',';').replace('\\\\','\\')
def ics_escape(s):return str(s).replace('\\','\\\\').replace('\n','\\n').replace(',','\\,').replace(';','\\;')
def parse_ics(text):
    """UTC/date-only/plain-offset VEVENT only. TZID local times must use full libical/ICAL.js adapter."""
    events=[];v=None
    for ln in unfold(text).splitlines():
        if ln=='BEGIN:VEVENT': v={};continue
        if ln=='END:VEVENT':
            if v and {'UID','SUMMARY','DTSTART','DTEND'}<=v.keys():
                def conv(value):
                    if len(value)==8:return datetime.strptime(value,'%Y%m%d').replace(tzinfo=timezone.utc).isoformat(),1
                    if value.endswith('Z'):return datetime.strptime(value,'%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc).isoformat(),0
                    raise InputError('VEVENT mit lokaler Zeit/TZID wird nicht ohne Zeitzonenbibliothek importiert.')
                start,all_day=conv(v['DTSTART']);end,_=conv(v['DTEND'])
                events.append({'uid':v['UID'][:240], 'title':ics_unescape(v['SUMMARY'])[:300],
                               'description':ics_unescape(v.get('DESCRIPTION',''))[:5000],
                               'starts_at':start,'ends_at':end,'location':ics_unescape(v.get('LOCATION',''))[:300],
                               'all_day':all_day, 'rrule':v.get('RRULE','')[:400]})
            v=None;continue
        if v is not None and ':' in ln:
            key,val=ln.split(':',1)
            if key.startswith(('DTSTART;TZID','DTEND;TZID')):raise InputError('TZID-Events erfordern einen vollständigen iCalendar-Parser.')
            v[key.split(';')[0]]=val
    return events

def export_ics(items):
    out=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//AVENIQ//Calendar//DE','CALSCALE:GREGORIAN']
    for e in items:
        def dt(v,all_day):
            d=datetime.fromisoformat(v.replace('Z','+00:00')).astimezone(timezone.utc)
            return (';VALUE=DATE:'+d.strftime('%Y%m%d')) if all_day else (':'+d.strftime('%Y%m%dT%H%M%SZ'))
        out.extend(['BEGIN:VEVENT','UID:'+str(e['uid']), 'DTSTAMP:'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'),
                    'SUMMARY:'+ics_escape(e['title']), 'DTSTART'+dt(e['starts_at'],e.get('all_day')),
                    'DTEND'+dt(e['ends_at'],e.get('all_day')), 'DESCRIPTION:'+ics_escape(e.get('description','')),
                    'LOCATION:'+ics_escape(e.get('location',''))])
        if e.get('rrule'):out.append('RRULE:'+e['rrule'])
        out.append('END:VEVENT')
    out.append('END:VCALENDAR')
    return '\r\n'.join(out)+'\r\n'

def caldav_sync(conn,calendar,limit=60):
    """Import via CalDAV PROPFIND+GET (read-only). No hidden edits to remote server."""
    url=calendar.get('dav_url','')
    parsed=urllib.parse.urlparse(url)
    if parsed.scheme!='https' or not parsed.netloc or parsed.username or parsed.password:
        raise InputError('CalDAV erfordert eine HTTPS-Kalender-Collection ohne eingebettete Zugangsdaten.')
    prefix=calendar.get('credential_prefix','').strip()
    user=os.getenv(prefix+'_USER','') if prefix else ''
    pw=os.getenv(prefix+'_PASSWORD','') if prefix else ''
    if not user or not pw:raise InputError('CalDAV-Zugangsdaten fehlen in der Serverumgebung.')
    auth='Basic '+base64.b64encode((user+':'+pw).encode()).decode()
    def request(target,method='GET',body=None,headers=None):
        req=urllib.request.Request(target,data=body,method=method,headers={'Authorization':auth,'User-Agent':'AVENIQ/0.1',**(headers or {})})
        with urllib.request.urlopen(req,timeout=25,context=ssl.create_default_context()) as r:
            content=r.read(3_000_001)
            if len(content)>3_000_000:raise InputError('CalDAV-Antwort zu groß.')
            return content
    body=b'<?xml version="1.0"?><d:propfind xmlns:d="DAV:"><d:prop><d:getetag/></d:prop></d:propfind>'
    xml=request(url,'PROPFIND',body,{'Depth':'1','Content-Type':'application/xml'})
    root=ET.fromstring(xml);ns={'d':'DAV:'}
    base=urllib.parse.urlparse(url)
    targets=[]
    for el in root.findall('.//d:response',ns):
        href=el.findtext('d:href',default='',namespaces=ns)
        if not href.lower().endswith('.ics'):continue
        target=urllib.parse.urljoin(url,href)
        p=urllib.parse.urlparse(target)
        # Only fetch files from same DAV collection origin and subtree.
        if p.scheme!=base.scheme or p.netloc!=base.netloc or not p.path.startswith(base.path.rstrip('/')+'/'):continue
        etag=el.findtext('.//d:getetag',default='',namespaces=ns)
        targets.append((target,etag))
    count=0
    for target,etag in targets[:limit]:
        exists=conn.execute('SELECT 1 FROM events WHERE calendar_id=? AND remote_href=? AND remote_etag=?',(calendar['id'],target,etag)).fetchone()
        if exists:continue
        text=request(target).decode('utf-8','replace')
        try:parsed_events=parse_ics(text)
        except InputError:continue
        for e in parsed_events:
            conn.execute('''INSERT INTO events(calendar_id,uid,title,description,starts_at,ends_at,location,all_day,rrule,remote_href,remote_etag,origin) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(calendar_id,uid) DO UPDATE SET title=excluded.title,description=excluded.description,starts_at=excluded.starts_at,ends_at=excluded.ends_at,location=excluded.location,all_day=excluded.all_day,rrule=excluded.rrule,remote_href=excluded.remote_href,remote_etag=excluded.remote_etag''',
            (calendar['id'],e['uid'],e['title'],e['description'],e['starts_at'],e['ends_at'],e['location'],e['all_day'],e['rrule'],target,etag,'dav_remote'))
            count+=1
    return count
