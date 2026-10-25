"""Local-first single-user HTTP API. Public/multi-user deployment requires hardening."""
from __future__ import annotations
import csv, hashlib, hmac, io, json, os, re, secrets, threading, time
from datetime import datetime, timezone
from email.utils import make_msgid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs,urlsplit
from . import __version__,db,mail,calendar,ai,security

ROOT=Path(__file__).resolve().parent.parent
WEB=ROOT/'web'
MAX_BODY=2_000_000
RUNNING=set();RUNLOCK=threading.Lock(); SENDLOCK=threading.Lock()
BADLOGINS={}; LOGINLOCK=threading.Lock()

class Handler(BaseHTTPRequestHandler):
    server_version='AVENIQ/'+__version__
    def log_message(self,fmt,*args):
        # No cookie/query credentials/body content in logs
        print('[AVENIQ]',fmt%args if '?' not in (fmt%args) else 'request',flush=True)
    def _reply(self,status,body,typ='application/json; charset=utf-8',extra=None):
        if typ.startswith('application/json') and not isinstance(body,(str,bytes)):body=json.dumps(body,ensure_ascii=False)
        raw=body.encode('utf-8') if isinstance(body,str) else body
        # Commit successful mutations BEFORE HTTP success becomes visible to another thread.
        if 200 <= int(status) < 400 and getattr(self,'_conn',None) is not None:
            self._conn.commit()
        self.send_response(status)
        for k,v in {'Content-Type':typ,'Content-Length':str(len(raw)),'X-Content-Type-Options':'nosniff',
                     'X-Frame-Options':'DENY','Referrer-Policy':'no-referrer','Cache-Control':'no-store',
                     'Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'",**(extra or {})}.items():self.send_header(k,v)
        self.end_headers();self.wfile.write(raw)
    def _json(self):
        try:length=int(self.headers.get('Content-Length','0'))
        except ValueError:raise security.InputError('Ungültiger Content-Length')
        if length<0 or length>MAX_BODY:raise security.InputError('Anfrage zu groß (max. 2 MB).')
        if not self.headers.get('Content-Type','').startswith('application/json'):raise security.InputError('JSON benötigt.')
        try:v=json.loads(self.rfile.read(length))
        except ValueError:raise security.InputError('Ungültiges JSON.')
        if not isinstance(v,dict):raise security.InputError('JSON-Objekt benötigt.')
        return v
    def _sess(self,c):
        t=security.cookie_get(self.headers)
        if not t:return None
        row=db.one(c.execute('SELECT * FROM sessions WHERE token_hash=? AND expires>?',(security.token_hash(t),int(time.time()))))
        return row
    def _auth(self,c,write=False):
        s=self._sess(c)
        if not s:raise PermissionError('Bitte anmelden.')
        if write:
            origin=self.headers.get('Origin','')
            allowed=os.getenv('AVENIQ_PUBLIC_ORIGIN','').rstrip('/')
            local={f'http://{self.headers.get("Host","")}',f'https://{self.headers.get("Host","")}'}
            if origin and origin not in local|({allowed} if allowed else set()):raise PermissionError('Ungültiger Origin.')
            if not hmac.compare_digest(self.headers.get('X-CSRF-Token',''),s['csrf']):raise PermissionError('CSRF-Token fehlt.')
        return s
    def _audit(self,c,kind,detail=''):
        c.execute('INSERT INTO audit(kind,detail) VALUES(?,?)',(kind,detail[:300]))
    def _project_data(self,body,keys):
        return {k:v for k,v in body.items() if k in keys}
    def _login(self,c,body,setup=False):
        email=security.email_address(body.get('email','')).lower()
        password=security.require_text(body.get('password',''),'Passwort',500)
        ip=self.client_address[0]
        if setup:
            if c.execute('SELECT 1 FROM users').fetchone():raise PermissionError('Konto existiert bereits.')
            hashed=security.hash_password(password)
            uid=c.execute('INSERT INTO users(email,password_hash) VALUES(?,?)',(email,hashed)).lastrowid
        else:
            with LOGINLOCK:
                recent=[x for x in BADLOGINS.get(ip,[]) if time.monotonic()-x<600]
                BADLOGINS[ip]=recent
                if len(recent)>=8:raise PermissionError('Zu viele Loginversuche. Später erneut versuchen.')
            row=db.one(c.execute('SELECT * FROM users WHERE email=?',(email,)))
            if not row or not security.check_password(password,row['password_hash']):
                with LOGINLOCK: BADLOGINS.setdefault(ip,[]).append(time.monotonic())
                raise PermissionError('E-Mail oder Passwort falsch.')
            uid=row['id']
            with LOGINLOCK:BADLOGINS.pop(ip,None)
        token=security.token();csrf=security.token()
        c.execute('INSERT INTO sessions(token_hash,user_id,csrf,expires) VALUES(?,?,?,?)',(security.token_hash(token),uid,csrf,int(time.time())+604800))
        self._audit(c,'login',email)
        return self._reply(200,{'ok':True,'csrf':csrf},extra={'Set-Cookie':security.session_cookie(token)})
    def _static(self,path):
        mapping={'/':'index.html','/index.html':'index.html','/app.js':'app.js','/styles.css':'styles.css','/manifest.webmanifest':'manifest.webmanifest','/favicon.svg':'favicon.svg','/sw.js':'sw.js'}
        if path not in mapping:return self._reply(404,{'error':'Nicht gefunden'})
        mime={'.html':'text/html; charset=utf-8','.js':'application/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.svg':'image/svg+xml','.webmanifest':'application/manifest+json'}[Path(path).suffix or '.html']
        return self._reply(200,(WEB/mapping[path]).read_bytes(),mime)
    def do_GET(self):self._route('GET')
    def do_POST(self):self._route('POST')
    def do_PATCH(self):self._route('PATCH')
    def do_DELETE(self):self._route('DELETE')
    def _route(self,method):
        parsed=urlsplit(self.path);path=parsed.path;query=parse_qs(parsed.query)
        if not path.startswith('/api/'):
            return self._static(path) if method=='GET' else self._reply(405,{'error':'Nicht erlaubt'})
        try:
            with db.connect(self.server.database) as c:
                self._conn=c
                if path=='/api/health' and method=='GET':
                    return self._reply(200,{'version':__version__,'initialized':bool(c.execute('SELECT 1 FROM users').fetchone())})
                if path=='/api/setup' and method=='POST':return self._login(c,self._json(),True)
                if path=='/api/login' and method=='POST':return self._login(c,self._json(),False)
                if path=='/api/session' and method=='GET':
                    s=self._sess(c)
                    return self._reply(200,{'authenticated':bool(s),'csrf':s['csrf'] if s else ''})
                self._auth(c,write=method!='GET')
                if path=='/api/logout' and method=='POST':
                    c.execute('DELETE FROM sessions WHERE token_hash=?',(security.token_hash(security.cookie_get(self.headers)),))
                    return self._reply(200,{'ok':True},extra={'Set-Cookie':security.session_cookie('',0)})
                if path=='/api/dashboard' and method=='GET':
                    counters={t:c.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t in ('messages','events','contacts','tasks','accounts')}
                    counters['unread']=c.execute('SELECT COUNT(*) FROM messages WHERE unread=1 AND archived=0').fetchone()[0]
                    counters['open_tasks']=c.execute('SELECT COUNT(*) FROM tasks WHERE completed=0').fetchone()[0]
                    counters['next_events']=db.rows(c.execute('SELECT * FROM events WHERE ends_at>=? ORDER BY starts_at LIMIT 5',(datetime.now(timezone.utc).isoformat(),)))
                    return self._reply(200,counters)
                if path=='/api/accounts':
                    if method=='GET':return self._reply(200,db.rows(c.execute('SELECT id,name,email,imap_host,imap_port,smtp_host,smtp_port,credential_prefix,enabled,sync_error,last_sync FROM accounts ORDER BY id')))
                    if method=='POST':
                        b=self._json()
                        email=security.email_address(b.get('email',''))
                        host=re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9.\-]{0,250}$')
                        imap=security.require_text(b.get('imap_host',''),'IMAP-Host',250)
                        smtp=security.require_text(b.get('smtp_host',''),'SMTP-Host',250)
                        if not host.fullmatch(imap) or not host.fullmatch(smtp):raise security.InputError('Ungültiger Host.')
                        prefix=security.require_text(b.get('credential_prefix',''),'ENV-Prefix',90)
                        if not re.fullmatch(r'AVENIQ_ACCOUNT_[A-Z0-9_]+',prefix):raise security.InputError('ENV-Prefix: AVENIQ_ACCOUNT_*')
                        ip=int(b.get('imap_port',993));sp=int(b.get('smtp_port',587))
                        if ip!=993 or sp not in (465,587):raise security.InputError('Nur IMAPS 993 und SMTPS 465 / STARTTLS 587.')
                        id=c.execute('INSERT INTO accounts(name,email,imap_host,imap_port,smtp_host,smtp_port,credential_prefix) VALUES(?,?,?,?,?,?,?)',
                         (security.require_text(b.get('name',''),'Name',120),email,imap,ip,smtp,sp,prefix)).lastrowid
                        return self._reply(201,{'id':id})
                match=re.fullmatch(r'/api/accounts/(\d+)(/sync)?',path)
                if match:
                    id=int(match[1]);a=db.one(c.execute('SELECT * FROM accounts WHERE id=?',(id,)))
                    if not a:return self._reply(404,{'error':'Konto fehlt'})
                    if match[2]=='/sync' and method=='POST':
                        with RUNLOCK:
                            if id in RUNNING:raise security.InputError('Synchronisation läuft bereits.')
                            RUNNING.add(id)
                        try:
                            # Read-only fetch + app cache. SQLite transaction is rolled back on IMAP error.
                            imported=mail.sync_inbox(c,a,150)
                            c.execute("UPDATE accounts SET last_sync=CURRENT_TIMESTAMP,sync_error='' WHERE id=?",(id,))
                            self._audit(c,'imap_sync',str(id)+' imported '+str(imported))
                            return self._reply(200,{'imported':imported})
                        except Exception as e:
                            c.execute('UPDATE accounts SET sync_error=? WHERE id=?',(str(e)[:300],id))
                            raise
                        finally:
                            with RUNLOCK:RUNNING.discard(id)
                    if match[2] is None and method=='DELETE':
                        c.execute('DELETE FROM accounts WHERE id=?',(id,));return self._reply(200,{'ok':True})
                if path=='/api/messages' and method=='GET':
                    folder=query.get('folder',['all'])[0]
                    allowed={'all','inbox','starred','archive','sent'}
                    if folder not in allowed:raise security.InputError('Unbekannter Filter.')
                    wh={'all':'1=1','inbox':'archived=0 AND folder="INBOX"','starred':'starred=1','archive':'archived=1','sent':'folder="Sent"'}[folder]
                    account=query.get('account',[''])[0]
                    args=[]
                    if account.isdigit(): wh+=' AND account_id=?';args.append(int(account))
                    q=query.get('q',[''])[0][:200]
                    if q:
                        try:
                            sql=f'''SELECT m.* FROM messages m JOIN message_search s ON s.rowid=m.id WHERE {wh.replace('archived','m.archived').replace('folder','m.folder').replace('starred','m.starred').replace('account_id','m.account_id')} AND message_search MATCH ? ORDER BY m.id DESC LIMIT 200'''
                            items=db.rows(c.execute(sql,args+[security.safe_fts(q)]))
                        except Exception:items=[]
                    else:items=db.rows(c.execute(f'SELECT * FROM messages WHERE {wh} ORDER BY id DESC LIMIT 300',args))
                    return self._reply(200,[{k:v for k,v in item.items() if k!='body'} for item in items])
                if path=='/api/messages/demo' and method=='POST':
                    if c.execute("SELECT 1 FROM messages WHERE source='demo'").fetchone():raise security.InputError('Demo-Daten wurden schon geladen.')
                    samples=[('Studio Fjell','hello@studio-fjell.example','Nächste Schritte zum Projekt','Wir haben die ersten Entwürfe geprüft. Können wir am Donnerstag einen Termin vereinbaren?'),
                             ('Büro Nord','team@bueronord.example','Angebot und Zeitplan','Vielen Dank! Wir prüfen den Vorschlag und melden uns bis Ende der Woche.'),
                             ('Klara W.','klara@example.test','Unterlagen zum Workshop','Hallo, die Unterlagen sind da. Bitte noch den Termin bestätigen.'),
                             ('Kalender-Service','noreply@example.test','Neue Einladung','Einladung: Abstimmung zum Sprint, kommenden Montag um 10 Uhr.')]
                    for idx,(name,sender,subject,body) in enumerate(samples):
                        c.execute('INSERT INTO messages(folder,subject,sender,recipients,body,preview,source,unread) VALUES(?,?,?,?,?,?,?,?)',
                                  ('INBOX',subject,f'{name} <{sender}>','ich@example.test',body,body[:160],'demo',1 if idx<2 else 0))
                    self._audit(c,'demo_insert','4 synthetic messages')
                    return self._reply(201,{'imported':len(samples)})
                match=re.fullmatch(r'/api/messages/(\d+)',path)
                if match:
                    id=int(match[1]);m=db.one(c.execute('SELECT * FROM messages WHERE id=?',(id,)))
                    if not m:return self._reply(404,{'error':'Nachricht fehlt'})
                    if method=='GET':return self._reply(200,m)
                    if method=='PATCH':
                        b=self._json();changes={k:int(v) for k,v in b.items() if k in ('unread','starred','archived') and isinstance(v,bool)}
                        if not changes:raise security.InputError('Keine gültigen Änderungen.')
                        sql=','.join(k+'=?' for k in changes)
                        c.execute(f'UPDATE messages SET {sql} WHERE id=?',(*changes.values(),id))
                        # local-only state; remote IMAP flags are NOT changed.
                        return self._reply(200,{'ok':True,'local_only':True})
                if path=='/api/drafts':
                    if method=='GET':return self._reply(200,db.rows(c.execute('SELECT * FROM drafts ORDER BY id DESC LIMIT 100')))
                    if method=='POST':
                        b=self._json()
                        aid=b.get('account_id');aid=int(aid) if aid else None
                        if aid and not c.execute('SELECT 1 FROM accounts WHERE id=?',(aid,)).fetchone():raise security.InputError('Konto fehlt.')
                        subj=security.clean_text(b.get('subject',''),300);body=security.clean_text(b.get('body',''),150000)
                        if not subj or not body:raise security.InputError('Betreff und Text fehlen.')
                        to=security.email_address(b.get('to_addr',''))
                        ident=c.execute('INSERT INTO drafts(account_id,to_addr,subject,body) VALUES(?,?,?,?)',(aid,to,subj,body)).lastrowid
                        return self._reply(201,{'id':ident})
                match=re.fullmatch(r'/api/drafts/(\d+)(/send)?',path)
                if match:
                    id=int(match[1]);d=db.one(c.execute('SELECT * FROM drafts WHERE id=?',(id,)))
                    if not d:return self._reply(404,{'error':'Entwurf fehlt.'})
                    if match[2] is None and method=='PATCH':
                        if d['state']!='draft':raise security.InputError('Nur ungesendete Entwürfe sind bearbeitbar.')
                        b=self._json();vals={k:security.clean_text(v,150000 if k=='body' else 300) for k,v in b.items() if k in ('subject','body')}
                        if 'to_addr' in b:vals['to_addr']=security.email_address(b['to_addr'])
                        if vals:c.execute('UPDATE drafts SET '+','.join(k+'=?' for k in vals)+' WHERE id=?',(*vals.values(),id))
                        return self._reply(200,{'ok':True})
                    if match[2] is None and method=='DELETE':
                        if d['state']!='draft':raise security.InputError('Versandhistorie kann nicht still gelöscht werden.')
                        c.execute('DELETE FROM drafts WHERE id=?',(id,));return self._reply(200,{'ok':True})
                    if match[2]=='/send' and method=='POST':
                        b=self._json()
                        if b.get('confirmation')!='SEND_NOW':raise security.InputError('Explizite Versandbestätigung erforderlich.')
                        if not d['account_id']:raise security.InputError('Bitte Absenderkonto auswählen.')
                        a=db.one(c.execute('SELECT * FROM accounts WHERE id=?',(d['account_id'],)))
                        if not a:raise security.InputError('Absenderkonto fehlt.')
                        with SENDLOCK:
                            r=c.execute("UPDATE drafts SET state='sending',message_id=? WHERE id=? AND state='draft'",(make_msgid(domain=a['email'].split('@')[-1]),id))
                            if r.rowcount!=1:raise security.InputError('Nachricht wurde schon gesendet oder verarbeitet.')
                            c.commit(); d=db.one(c.execute('SELECT * FROM drafts WHERE id=?',(id,)))
                        try:
                            mail.send(a,d['to_addr'],d['subject'],d['body'],d['message_id'])
                            c.execute("UPDATE drafts SET state='sent',sent_at=CURRENT_TIMESTAMP,error='' WHERE id=?",(id,))
                            c.execute('INSERT INTO messages(account_id,folder,message_id,subject,sender,recipients,body,preview,source,unread) VALUES(?,?,?,?,?,?,?,?,?,0)',
                                      (a['id'],'Sent',d['message_id'],d['subject'],a['email'],d['to_addr'],d['body'],d['body'][:180],'smtp'))
                            self._audit(c,'smtp_sent',str(id))
                            return self._reply(200,{'ok':True})
                        except Exception:
                            # Delivery state may be uncertain; never silently resend.
                            c.execute("UPDATE drafts SET state='uncertain',error='SMTP-Zustand unklar. Vor erneutem Versand Gesendet-Ordner prüfen.' WHERE id=?",(id,))
                            c.commit()
                            raise
                if path=='/api/calendars':
                    if method=='GET':return self._reply(200,db.rows(c.execute('SELECT * FROM calendars ORDER BY id')))
                    if method=='POST':
                        b=self._json();name=security.require_text(b.get('name',''),'Kalendername',100)
                        url=security.clean_text(b.get('dav_url',''),600)
                        prefix=security.clean_text(b.get('credential_prefix',''),100)
                        if url and (not url.startswith('https://') or not re.fullmatch('AVENIQ_CAL_[A-Z0-9_]+',prefix)):
                            raise security.InputError('CalDAV benötigt HTTPS und AVENIQ_CAL_* als ENV-Prefix.')
                        color=security.clean_text(b.get('color','#66b9a5'),10)
                        if not re.fullmatch('#[0-9a-fA-F]{6}',color):raise security.InputError('Hex-Farbcode erwartet.')
                        id=c.execute('INSERT INTO calendars(name,color,dav_url,credential_prefix) VALUES(?,?,?,?)',(name,color,url,prefix)).lastrowid
                        return self._reply(201,{'id':id})
                match=re.fullmatch(r'/api/calendars/(\d+)/sync',path)
                if match and method=='POST':
                    cal=db.one(c.execute('SELECT * FROM calendars WHERE id=?',(int(match[1]),)))
                    if not cal or not cal['dav_url']:raise security.InputError('Kein CalDAV-Kalender.')
                    added=calendar.caldav_sync(c,cal)
                    c.execute('UPDATE calendars SET sync_error="",last_sync=CURRENT_TIMESTAMP WHERE id=?',(cal['id'],))
                    return self._reply(200,{'imported_or_updated':added,'read_only':True})
                if path=='/api/events':
                    if method=='GET':
                        start=query.get('start',[''])[0];end=query.get('end',[''])[0]
                        if start and end:
                            return self._reply(200,db.rows(c.execute('SELECT e.*,c.name AS calendar_name,c.color FROM events e JOIN calendars c ON c.id=e.calendar_id WHERE ends_at>=? AND starts_at<=? ORDER BY starts_at LIMIT 1000',(start,end))))
                        return self._reply(200,db.rows(c.execute('SELECT e.*,c.name AS calendar_name,c.color FROM events e JOIN calendars c ON c.id=e.calendar_id ORDER BY starts_at LIMIT 1000')))
                    if method=='POST':
                        b=self._json();eid=self._event_save(c,b)
                        return self._reply(201,{'id':eid})
                match=re.fullmatch(r'/api/events/(\d+)',path)
                if match:
                    event=db.one(c.execute('SELECT * FROM events WHERE id=?',(int(match[1]),)))
                    if not event:return self._reply(404,{'error':'Termin fehlt.'})
                    if event['origin']=='dav_remote':raise security.InputError('Remote-Kalender ist in dieser Version nur lesbar.')
                    if method=='DELETE':c.execute('DELETE FROM events WHERE id=?',(event['id'],));return self._reply(200,{'ok':True})
                    if method=='PATCH':
                        b=self._json();eid=self._event_save(c,{**event,**b},event['id']);return self._reply(200,{'id':eid})
                if path=='/api/ics':
                    if method=='GET':
                        items=db.rows(c.execute('SELECT * FROM events ORDER BY starts_at LIMIT 10000'))
                        return self._reply(200,calendar.export_ics(items),'text/calendar; charset=utf-8',{'Content-Disposition':'attachment; filename="aveniq.ics"'})
                    if method=='POST':
                        b=self._json();cid=int(b.get('calendar_id',1))
                        rows=calendar.parse_ics(security.require_text(b.get('ics',''),'iCalendar',500000))
                        count=0
                        for event in rows:
                            self._event_save(c,{**event,'calendar_id':cid});count+=1
                        return self._reply(200,{'imported':count})
                if path=='/api/contacts':
                    if method=='GET':return self._reply(200,db.rows(c.execute('SELECT * FROM contacts ORDER BY name COLLATE NOCASE LIMIT 2000')))
                    if method=='POST':return self._simple_create(c,'contacts',('name','email','phone','company','notes'),self._json())
                if path=='/api/tasks':
                    if method=='GET':return self._reply(200,db.rows(c.execute('SELECT * FROM tasks ORDER BY completed,due_at,id LIMIT 1000')))
                    if method=='POST':return self._simple_create(c,'tasks',('title','notes','due_at','priority','completed'),self._json())
                match=re.fullmatch(r'/api/(contacts|tasks)/(\d+)',path)
                if match:
                    table,id=match[1],int(match[2]);row=db.one(c.execute(f'SELECT * FROM {table} WHERE id=?',(id,)))
                    if not row:return self._reply(404,{'error':'Eintrag fehlt.'})
                    if method=='DELETE':c.execute(f'DELETE FROM {table} WHERE id=?',(id,));return self._reply(200,{'ok':True})
                    if method=='PATCH':
                        allowed=('name','email','phone','company','notes') if table=='contacts' else ('title','notes','due_at','priority','completed')
                        b={k:self._clean_field(k,v) for k,v in self._json().items() if k in allowed}
                        if b:c.execute(f'UPDATE {table} SET '+','.join(k+'=?' for k in b)+' WHERE id=?',(*b.values(),id))
                        return self._reply(200,{'ok':True})
                if path=='/api/settings':
                    if method=='GET':
                        return self._reply(200,{'ai_enabled':json.loads(c.execute("SELECT value FROM settings WHERE key='ai_enabled'").fetchone()[0]),
                            'ai_provider_configured':bool(os.getenv('AVENIQ_OPENAI_API_KEY')),
                            'privacy':'Keine externe KI-Anfrage ohne globale Aktivierung und separate Einzelfreigabe.',
                            'external_data_sent_by_default':False})
                    if method=='PATCH':
                        b=self._json()
                        if not isinstance(b.get('ai_enabled'),bool):raise security.InputError('Booleschen KI-Schalter setzen.')
                        if b['ai_enabled'] and b.get('ack')!='I_EXPLICITLY_OPT_IN_TO_AI':raise security.InputError('Explizite KI-Einwilligung erforderlich.')
                        c.execute("UPDATE settings SET value=? WHERE key='ai_enabled'",('true' if b['ai_enabled'] else 'false',))
                        self._audit(c,'ai_opt_in' if b['ai_enabled'] else 'ai_opt_out','')
                        return self._reply(200,{'enabled':b['ai_enabled']})
                if path=='/api/ai' and method=='POST':
                    b=self._json();on=json.loads(c.execute("SELECT value FROM settings WHERE key='ai_enabled'").fetchone()[0])
                    result=ai.run(b.get('task'),b.get('text'),b.get('consent'),on)
                    self._audit(c,'ai_action',str(b.get('task')))
                    return self._reply(200,{'result':result,'sent_to_provider':True,'automatically_saved':False})
                if path=='/api/audit' and method=='GET':return self._reply(200,db.rows(c.execute('SELECT * FROM audit ORDER BY id DESC LIMIT 80')))
                return self._reply(404,{'error':'Endpunkt nicht gefunden.'})
        except PermissionError as e:self._reply(403,{'error':str(e)})
        except (security.InputError,ValueError,KeyError) as e:self._reply(400,{'error':str(e)})
        except (mail.MailConnectionError,ai.AIUnavailable) as e:self._reply(502,{'error':str(e)})
        except Exception as e:
            print('SERVER ERROR',type(e).__name__,str(e)[:200],flush=True)
            self._reply(500,{'error':'Interner Fehler. Details im Serverlog.'})
    def _clean_field(self,k,v):
        if k in ('completed',):return int(bool(v))
        if k=='priority':
            p=int(v)
            if p not in (1,2,3):raise security.InputError('Priorität 1–3.')
            return p
        return security.clean_text(v,4000 if k=='notes' else 400)
    def _simple_create(self,c,table,fields,b):
        values={k:self._clean_field(k,b[k]) for k in fields if k in b}
        required='name' if table=='contacts' else 'title'
        if not values.get(required):raise security.InputError('Name/Titel fehlt.')
        if table=='contacts' and values.get('email'):values['email']=security.email_address(values['email'])
        id=c.execute(f'INSERT INTO {table}('+','.join(values)+') VALUES('+','.join('?' for _ in values)+')',tuple(values.values())).lastrowid
        return self._reply(201,{'id':id})
    def _event_save(self,c,b,id=None):
        title=security.require_text(b.get('title',''),'Termintitel',300)
        start=security.iso_dt(b.get('starts_at',''));end=security.iso_dt(b.get('ends_at',''))
        if datetime.fromisoformat(end)<=datetime.fromisoformat(start):raise security.InputError('Ende muss nach Beginn liegen.')
        cid=int(b.get('calendar_id',1))
        if not c.execute('SELECT 1 FROM calendars WHERE id=?',(cid,)).fetchone():raise security.InputError('Kalender fehlt.')
        data=(cid,security.require_text(b.get('uid') or secrets.token_urlsafe(14),'UID',240),title,
              security.clean_text(b.get('description',''),5000),start,end,security.clean_text(b.get('location',''),300),
              int(bool(b.get('all_day',False))),security.clean_text(b.get('rrule',''),400))
        if id:
            c.execute('UPDATE events SET calendar_id=?,uid=?,title=?,description=?,starts_at=?,ends_at=?,location=?,all_day=?,rrule=? WHERE id=?',(*data,id));return id
        existing=c.execute('SELECT id FROM events WHERE calendar_id=? AND uid=?',(cid,data[1])).fetchone()
        if existing:
            id=existing[0];c.execute('UPDATE events SET title=?,description=?,starts_at=?,ends_at=?,location=?,all_day=?,rrule=? WHERE id=?',(*data[2:],id));return id
        return c.execute('INSERT INTO events(calendar_id,uid,title,description,starts_at,ends_at,location,all_day,rrule) VALUES(?,?,?,?,?,?,?,?,?)',data).lastrowid

def run():
    dbpath=db.initialize();host=os.getenv('AVENIQ_HOST','127.0.0.1');port=int(os.getenv('AVENIQ_PORT','8768'))
    # The first account must be created on loopback before reverse-proxy exposure.
    with db.connect(dbpath) as c:
        count=c.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    if not count and host not in ('127.0.0.1','localhost','::1') and os.getenv('AVENIQ_ALLOW_REMOTE_SETUP')!='I_ACCEPT_THE_RISK':
        raise RuntimeError('Ersteinrichtung muss auf Loopback erfolgen. AVENIQ_HOST=127.0.0.1 verwenden.')
    server=ThreadingHTTPServer((host,port),Handler);server.database=dbpath
    print(f'AVENIQ {__version__}: http://{host}:{port} (DB: {dbpath})',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':run()
