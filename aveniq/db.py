"""SQLite persistence, migrations and FTS5 search. One operator per installation."""
from __future__ import annotations
import os, sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = lambda: Path(os.getenv('AVENIQ_DB', './data/aveniq.db')).resolve()
SCHEMA = '''
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS sessions (token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, csrf TEXT NOT NULL, expires INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL, imap_host TEXT NOT NULL, imap_port INTEGER NOT NULL DEFAULT 993, smtp_host TEXT NOT NULL, smtp_port INTEGER NOT NULL DEFAULT 587, credential_prefix TEXT NOT NULL, enabled INTEGER NOT NULL DEFAULT 1, sync_error TEXT DEFAULT '', last_sync TEXT, UNIQUE(email, credential_prefix));
CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE, folder TEXT NOT NULL DEFAULT 'INBOX', remote_uid TEXT, message_id TEXT, subject TEXT NOT NULL DEFAULT '', sender TEXT NOT NULL DEFAULT '', recipients TEXT NOT NULL DEFAULT '', sent_at TEXT NOT NULL DEFAULT '', preview TEXT NOT NULL DEFAULT '', body TEXT NOT NULL DEFAULT '', unread INTEGER NOT NULL DEFAULT 1, starred INTEGER NOT NULL DEFAULT 0, archived INTEGER NOT NULL DEFAULT 0, labels TEXT NOT NULL DEFAULT '', source TEXT NOT NULL DEFAULT 'local', created_at TEXT DEFAULT CURRENT_TIMESTAMP, UNIQUE(account_id,folder,remote_uid));
CREATE TABLE IF NOT EXISTS drafts (id INTEGER PRIMARY KEY, account_id INTEGER REFERENCES accounts(id), to_addr TEXT NOT NULL DEFAULT '', subject TEXT NOT NULL DEFAULT '', body TEXT NOT NULL DEFAULT '', state TEXT NOT NULL DEFAULT 'draft' CHECK(state IN ('draft','sending','sent','uncertain')), message_id TEXT, sent_at TEXT, error TEXT NOT NULL DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS calendars (id INTEGER PRIMARY KEY, name TEXT NOT NULL, color TEXT NOT NULL DEFAULT '#64b6aa', dav_url TEXT NOT NULL DEFAULT '', credential_prefix TEXT NOT NULL DEFAULT '', sync_error TEXT NOT NULL DEFAULT '', last_sync TEXT);
CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, calendar_id INTEGER NOT NULL REFERENCES calendars(id) ON DELETE CASCADE, uid TEXT NOT NULL, title TEXT NOT NULL, description TEXT NOT NULL DEFAULT '', starts_at TEXT NOT NULL, ends_at TEXT NOT NULL, location TEXT NOT NULL DEFAULT '', all_day INTEGER NOT NULL DEFAULT 0, rrule TEXT NOT NULL DEFAULT '', remote_href TEXT NOT NULL DEFAULT '', remote_etag TEXT NOT NULL DEFAULT '', origin TEXT NOT NULL DEFAULT 'local', created_at TEXT DEFAULT CURRENT_TIMESTAMP, UNIQUE(calendar_id,uid));
CREATE TABLE IF NOT EXISTS contacts (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL DEFAULT '', phone TEXT NOT NULL DEFAULT '', company TEXT NOT NULL DEFAULT '', notes TEXT NOT NULL DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT NOT NULL, notes TEXT NOT NULL DEFAULT '', due_at TEXT NOT NULL DEFAULT '', priority INTEGER NOT NULL DEFAULT 2, completed INTEGER NOT NULL DEFAULT 0, message_id INTEGER REFERENCES messages(id) ON DELETE SET NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY, kind TEXT NOT NULL, detail TEXT NOT NULL DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE VIRTUAL TABLE IF NOT EXISTS message_search USING fts5(subject, sender, recipients, body, content='messages', content_rowid='id', tokenize='unicode61');
CREATE TRIGGER IF NOT EXISTS msg_ai AFTER INSERT ON messages BEGIN INSERT INTO message_search(rowid,subject,sender,recipients,body) VALUES (new.id,new.subject,new.sender,new.recipients,new.body); END;
CREATE TRIGGER IF NOT EXISTS msg_ad AFTER DELETE ON messages BEGIN INSERT INTO message_search(message_search,rowid,subject,sender,recipients,body) VALUES ('delete',old.id,old.subject,old.sender,old.recipients,old.body); END;
CREATE TRIGGER IF NOT EXISTS msg_au AFTER UPDATE OF subject,sender,recipients,body ON messages BEGIN INSERT INTO message_search(message_search,rowid,subject,sender,recipients,body) VALUES ('delete',old.id,old.subject,old.sender,old.recipients,old.body); INSERT INTO message_search(rowid,subject,sender,recipients,body) VALUES (new.id,new.subject,new.sender,new.recipients,new.body); END;
'''

def initialize(path=None):
    path = Path(path or DB_PATH()); path.parent.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(path)
    try:
        con.executescript(SCHEMA)
        con.execute("INSERT OR IGNORE INTO settings(key,value) VALUES('ai_enabled','false')")
        con.execute("INSERT OR IGNORE INTO settings(key,value) VALUES('ai_notice_version','1')")
        con.execute("INSERT OR IGNORE INTO calendars(name) SELECT 'Privat' WHERE NOT EXISTS(SELECT 1 FROM calendars)")
        con.commit()
    finally:con.close()
    return path

@contextmanager
def connect(path=None):
    con=sqlite3.connect(path or DB_PATH(),timeout=15); con.row_factory=sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON'); con.execute('PRAGMA busy_timeout=15000')
    try:
        yield con; con.commit()
    except Exception:
        con.rollback(); raise
    finally: con.close()

def rows(cursor): return [dict(r) for r in cursor.fetchall()]
def one(cursor):
    r=cursor.fetchone(); return dict(r) if r is not None else None
