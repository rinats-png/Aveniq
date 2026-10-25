"""IMAP UID-based snapshot sync and explicit SMTP send. No hidden networking."""
from __future__ import annotations
import imaplib, smtplib, ssl, os
from email import policy
from email.parser import BytesParser
from email.message import EmailMessage
from email.utils import parseaddr, parsedate_to_datetime, make_msgid
from pathlib import Path
from .security import InputError,email_address

class MailConnectionError(RuntimeError): pass

def credentials(account, kind):
    """Credentials are never stored in SQLite or exposed to browser. ENV prefix per account."""
    prefix=account['credential_prefix']
    user=os.getenv(prefix+'_USER',''); password=os.getenv(prefix+'_PASSWORD','')
    if not user or not password: raise MailConnectionError(f'{prefix}_USER und {prefix}_PASSWORD fehlen in der Serverumgebung.')
    return user,password

def _body_plain(msg):
    # Never render remote HTML: no tracking pixels, scripts or event handlers.
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type()=='text/plain' and part.get_content_disposition() != 'attachment':
                try:return str(part.get_content())[:100000]
                except Exception: pass
        return '[Nur HTML-Inhalt vorhanden. Aus Sicherheitsgründen nicht gerendert.]'
    if msg.get_content_type()=='text/plain':
        try:return str(msg.get_content())[:100000]
        except Exception:pass
    return '[Kein anzeigbarer Klartext]'

def parse_message(raw):
    msg=BytesParser(policy=policy.default).parsebytes(raw)
    try: sent=parsedate_to_datetime(str(msg['Date'])).isoformat() if msg['Date'] else ''
    except Exception: sent=''
    body=_body_plain(msg)
    return {'subject':str(msg['Subject'] or ''), 'sender':str(msg['From'] or ''),
            'recipients':str(msg['To'] or ''),'sent_at':sent,'body':body,
            'preview':' '.join(body.split())[:180], 'message_id':str(msg['Message-ID'] or '')}

def sync_inbox(conn, account, max_messages=100):
    """Fetch recent UIDs from INBOX only; idempotent append, no destructive changes."""
    username,password=credentials(account,'imap')
    client=None; imported=0
    try:
        client=imaplib.IMAP4_SSL(account['imap_host'],int(account['imap_port']),ssl_context=ssl.create_default_context(),timeout=25)
        client.login(username,password)
        status,_=client.select('INBOX',readonly=True)
        if status!='OK':raise MailConnectionError('INBOX nicht auswählbar.')
        status,data=client.uid('search',None,'ALL')
        if status!='OK':raise MailConnectionError('UID-Suche fehlgeschlagen.')
        uids=(data[0] or b'').split()[-max(1,min(int(max_messages),300)):]
        for uid in uids:
            remote=uid.decode('ascii')
            if conn.execute("SELECT 1 FROM messages WHERE account_id=? AND folder='INBOX' AND remote_uid=?",(account['id'],remote)).fetchone():continue
            status,parts=client.uid('fetch',uid,'(BODY.PEEK[] FLAGS)')
            if status!='OK':continue
            raw=next((p[1] for p in parts if isinstance(p,tuple) and isinstance(p[1],bytes)),None)
            if raw is None or len(raw)>12_000_000:continue
            parsed=parse_message(raw)
            # Can't safely assume unread state without parsing FLAGS; default to unread.
            conn.execute('''INSERT OR IGNORE INTO messages(account_id,folder,remote_uid,message_id,subject,sender,recipients,sent_at,body,preview,source)
                VALUES(?,?,?,?,?,?,?,?,?,?,?)''',(account['id'],'INBOX',remote,parsed['message_id'],parsed['subject'],parsed['sender'],parsed['recipients'],parsed['sent_at'],parsed['body'],parsed['preview'],'imap'))
            imported+=1
        return imported
    except (imaplib.IMAP4.error,OSError,ssl.SSLError) as exc:
        raise MailConnectionError(f'IMAP fehlgeschlagen: {type(exc).__name__}') from exc
    finally:
        if client:
            try:client.logout()
            except Exception:pass

def send(account,to_addr,subject,body,message_id=None):
    to_addr=email_address(to_addr)
    if '\n' in subject or '\r' in subject: raise InputError('Ungültiger Betreff.')
    username,password=credentials(account,'smtp')
    msg=EmailMessage()
    msg['From']=email_address(account['email']);msg['To']=to_addr;msg['Subject']=subject
    msg['Message-ID']=message_id or make_msgid(domain=account['email'].split('@')[-1]);msg.set_content(body)
    host=account['smtp_host'];port=int(account['smtp_port'])
    try:
        if port==465:
            with smtplib.SMTP_SSL(host,port,context=ssl.create_default_context(),timeout=25) as smtp:
                smtp.login(username,password);smtp.send_message(msg)
        else:
            with smtplib.SMTP(host,port,timeout=25) as smtp:
                smtp.ehlo();smtp.starttls(context=ssl.create_default_context());smtp.ehlo()
                smtp.login(username,password);smtp.send_message(msg)
        return msg['Message-ID']
    except (smtplib.SMTPException,OSError,ssl.SSLError) as exc:
        raise MailConnectionError('SMTP-Übertragung gescheitert oder unklar. Vor erneutem Versuch den Gesendet-Ordner kontrollieren.') from exc
