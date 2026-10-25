"""Auth helpers and protection from accidental data disclosure."""
import base64, hashlib, hmac, json, secrets, time
from http.cookies import SimpleCookie

class InputError(ValueError): pass

def require_text(v, name='Wert', maxlen=1000):
    if not isinstance(v,str) or not v.strip() or len(v)>maxlen: raise InputError(f'{name} fehlt oder ist zu lang (max. {maxlen}).')
    return v.strip()

def hash_password(p):
    if len(p)<12: raise InputError('Passwort benötigt mindestens 12 Zeichen.')
    salt=secrets.token_bytes(16)
    return base64.b64encode(salt+hashlib.scrypt(p.encode(),salt=salt,n=2**14,r=8,p=1)).decode()

def check_password(p,h):
    try:
        raw=base64.b64decode(h,validate=True); key=hashlib.scrypt(p.encode(),salt=raw[:16],n=2**14,r=8,p=1)
        return hmac.compare_digest(raw[16:],key)
    except (ValueError,TypeError): return False

def token():return secrets.token_urlsafe(32)
def token_hash(t):return hashlib.sha256(t.encode()).hexdigest()
def cookie_get(headers,name='aveniq_session'):
    try:
        cookie=SimpleCookie();cookie.load(headers.get('Cookie',''))
        return cookie[name].value if name in cookie else ''
    except Exception: return ''

def session_cookie(t,max_age=604800):
    import os
    # Only mark Secure if the user has configured a TLS deployment.
    secure='; Secure' if os.getenv('AVENIQ_PUBLIC_ORIGIN','').startswith('https://') else ''
    return f'aveniq_session={t}; HttpOnly; SameSite=Strict; Path=/; Max-Age={max_age}{secure}'

def clean_text(s,maxlen=5000):
    if not isinstance(s,str):raise InputError('Text erwartet.')
    if len(s)>maxlen:raise InputError(f'Maximal {maxlen} Zeichen erlaubt.')
    return s.strip()

def email_address(s):
    from email.utils import parseaddr
    s=require_text(s,'E-Mail',320)
    real=parseaddr(s)[1]
    if real!=s or s.count('@')!=1 or ' ' in s or '\n' in s or '\r' in s or '.' not in s.split('@')[-1]:
        raise InputError('Ungültige E-Mail-Adresse.')
    return s

def iso_dt(s):
    from datetime import datetime
    s=require_text(s,'Datum',50)
    try:
        date=datetime.fromisoformat(s.replace('Z','+00:00'))
        if date.tzinfo is None:raise ValueError('timezone required')
        return date.isoformat()
    except ValueError as e:raise InputError('Datum muss ISO 8601 mit Zeitzone sein.') from e

def safe_fts(s):
    # Quoted single phrase avoids FTS query operators from user input.
    s=clean_text(s,200).replace('"','""')
    return f'"{s}"' if s else ''
