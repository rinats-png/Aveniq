import unittest, tempfile
from pathlib import Path
from aveniq import db,security,calendar,mail,ai

class CoreTests(unittest.TestCase):
  def test_password_scrypt(self):
    h=security.hash_password('very-secure-password!');self.assertTrue(security.check_password('very-secure-password!',h));self.assertFalse(security.check_password('wrong-password',h))
  def test_password_min(self):
    with self.assertRaises(security.InputError):security.hash_password('short')
  def test_email_rejects_crlf(self):
    with self.assertRaises(security.InputError):security.email_address('a@example.com\nBcc:evil@example.com')
  def test_iso_timezone_required(self):
    with self.assertRaises(security.InputError):security.iso_dt('2026-10-25T08:00:00')
  def test_ics_roundtrip(self):
    event={'uid':'e1','title':'Besprechung, Projekt','starts_at':'2026-11-10T08:30:00+00:00','ends_at':'2026-11-10T09:30:00+00:00','description':'Test\nText','location':'Frankfurt','all_day':0}
    data=calendar.export_ics([event]);parsed=calendar.parse_ics(data)
    self.assertEqual(len(parsed),1);self.assertEqual(parsed[0]['title'],event['title']);self.assertEqual(parsed[0]['description'],event['description'])
  def test_ics_rejects_tzid(self):
    content='BEGIN:VCALENDAR\nBEGIN:VEVENT\nUID:e2\nSUMMARY:Test\nDTSTART;TZID=Europe/Berlin:20261025T100000\nDTEND;TZID=Europe/Berlin:20261025T110000\nEND:VEVENT\nEND:VCALENDAR'
    with self.assertRaises(security.InputError):calendar.parse_ics(content)
  def test_mime_parse_plaintext(self):
    data=b'From: Fred <fred@example.com>\r\nTo: Alice <alice@example.com>\r\nSubject: Hallo\r\nDate: Sun, 25 Oct 2026 09:00:00 +0100\r\nContent-Type: text/plain; charset=utf-8\r\n\r\nHi Alice.'
    parsed=mail.parse_message(data);self.assertEqual(parsed['subject'],'Hallo');self.assertIn('Hi Alice',parsed['body'])
  def test_ai_disabled_even_when_user_consent(self):
    with self.assertRaises(security.InputError):ai.run('summarize','private message',True,False)
  def test_ai_requires_each_consent(self):
    with self.assertRaises(security.InputError):ai.run('summarize','private message',False,True)
  def test_db_fts(self):
    with tempfile.TemporaryDirectory() as folder:
      path=db.initialize(Path(folder)/'db.sqlite')
      with db.connect(path) as c:
        c.execute("INSERT INTO messages(subject,body) VALUES('Einladung','Die Sitzung beginnt morgen')")
        x=c.execute('SELECT rowid FROM message_search WHERE message_search MATCH ?',('"Sitzung"',)).fetchone()
        self.assertIsNotNone(x)
  def test_account_constraints(self):
    with tempfile.TemporaryDirectory() as folder:
      path=db.initialize(Path(folder)/'db.sqlite')
      with db.connect(path) as c:
        c.execute("INSERT INTO accounts(name,email,imap_host,smtp_host,credential_prefix) VALUES('work','a@example.de','imap.example.de','smtp.example.de','AVENIQ_ACCOUNT_WORK')")
        self.assertEqual(c.execute('SELECT COUNT(*) FROM accounts').fetchone()[0],1)
if __name__=='__main__':unittest.main()
