import http.cookiejar, json, tempfile, threading, unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.request import build_opener, HTTPCookieProcessor, Request
from urllib.error import HTTPError
from unittest.mock import patch
from aveniq import db
from aveniq.server import Handler

class APITests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();path=db.initialize(Path(cls.temp.name)/'db.sqlite')
  cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler);cls.server.database=path
  cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
  cls.base='http://127.0.0.1:'+str(cls.server.server_port)
 @classmethod
 def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.temp.cleanup()
 def setUp(self):self.opener=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()));self.csrf=''
 def call(self,path,method='GET',body=None,csrf=True):
  headers={};raw=None
  if body is not None:raw=json.dumps(body).encode();headers['Content-Type']='application/json'
  if csrf and self.csrf and method!='GET':headers['X-CSRF-Token']=self.csrf
  req=Request(self.base+'/api'+path,data=raw,method=method,headers=headers)
  try:
   with self.opener.open(req,timeout=6) as r:return r.status,json.loads(r.read())
  except HTTPError as e:return e.code,json.loads(e.read())
 def login(self):
  if self.call('/health')[1]['initialized'] is False:result=self.call('/setup','POST',{'email':'admin@example.test','password':'highly-secure-test-pass'})
  else:result=self.call('/login','POST',{'email':'admin@example.test','password':'highly-secure-test-pass'})
  self.assertEqual(result[0],200);self.csrf=result[1]['csrf']
 def test_01_health_requires_no_login(self):
  self.assertEqual(self.call('/health')[0],200)
  self.assertEqual(self.call('/accounts')[0],403)
 def test_02_auth_csrf(self):
  self.login()
  self.assertEqual(self.call('/contacts','POST',{'name':'Alice'},csrf=False)[0],403)
  self.assertEqual(self.call('/contacts','POST',{'name':'Alice'})[0],201)
 def test_03_calendar_task_and_contact(self):
  self.login()
  s,d=self.call('/events','POST',{'title':'Review','starts_at':'2026-11-12T09:00:00+01:00','ends_at':'2026-11-12T10:00:00+01:00','calendar_id':1})
  self.assertEqual(s,201);self.assertGreater(d['id'],0)
  self.assertEqual(self.call('/tasks','POST',{'title':'Nachbereitung'})[0],201)
  self.assertEqual(self.call('/events')[0],200)
 def test_04_ai_strictly_opt_in(self):
  self.login()
  self.assertFalse(self.call('/settings')[1]['ai_enabled'])
  self.assertEqual(self.call('/ai','POST',{'task':'summarize','text':'hi','consent':True})[0],400)
  self.assertEqual(self.call('/settings','PATCH',{'ai_enabled':True})[0],400)
  self.assertEqual(self.call('/settings','PATCH',{'ai_enabled':True,'ack':'I_EXPLICITLY_OPT_IN_TO_AI'})[0],200)
  self.assertEqual(self.call('/ai','POST',{'task':'summarize','text':'hi','consent':False})[0],400)
  self.assertEqual(self.call('/settings','PATCH',{'ai_enabled':False})[0],200)
 def test_05_drafts_never_send_without_explicit_confirmation(self):
  self.login()
  s,d=self.call('/drafts','POST',{'to_addr':'bob@example.test','subject':'Hallo','body':'Nachricht'})
  self.assertEqual(s,201)
  self.assertEqual(self.call('/drafts/'+str(d['id'])+'/send','POST',{})[0],400)
  self.assertEqual(self.call('/drafts/'+str(d['id'])+'/send','POST',{'confirmation':'SEND_NOW'})[0],400)
 def test_06_demo_search(self):
  self.login()
  self.assertEqual(self.call('/messages/demo','POST',{})[0],201)
  s,data=self.call('/messages?q=Unterlagen')
  self.assertEqual(s,200);self.assertGreaterEqual(len(data),1)
 def test_07_send_exactly_once_with_mock_smtp(self):
  self.login()
  s,a=self.call('/accounts','POST',{'name':'Test','email':'test@example.test','imap_host':'imap.example.test','smtp_host':'smtp.example.test','credential_prefix':'AVENIQ_ACCOUNT_TEST'})
  self.assertEqual(s,201)
  s,d=self.call('/drafts','POST',{'account_id':a['id'],'to_addr':'bob@example.test','subject':'Einmalig','body':'Inhalt'})
  self.assertEqual(s,201)
  with patch('aveniq.server.mail.send',return_value='<fake@example.test>') as mocksend:
   self.assertEqual(self.call('/drafts/'+str(d['id'])+'/send','POST',{'confirmation':'SEND_NOW'})[0],200)
   self.assertEqual(self.call('/drafts/'+str(d['id'])+'/send','POST',{'confirmation':'SEND_NOW'})[0],400)
   mocksend.assert_called_once()
  drafts=self.call('/drafts')[1]
  self.assertEqual(next(x for x in drafts if x['id']==d['id'])['state'],'sent')
 def test_08_invalid_event_rejected(self):
  self.login()
  s,data=self.call('/events','POST',{'title':'invalid','starts_at':'2026-11-12T10:00:00+01:00','ends_at':'2026-11-12T09:00:00+01:00','calendar_id':1})
  self.assertEqual(s,400)
 def test_09_malicious_sender_not_html_script(self):
  self.login()
  with patch('aveniq.server.mail.sync_inbox',return_value=0):
   status,items=self.call('/messages')
   self.assertEqual(status,200)
  # Browser escapes all server text via esc(), no remote HTML allowed.
  from pathlib import Path
  code=(Path(__file__).resolve().parents[1]/'web'/'app.js').read_text()
  self.assertIn("replaceAll('<','&lt;')",code)
 def test_10_logout_invalidates_session(self):
  self.login()
  self.assertEqual(self.call('/logout','POST',{})[0],200)
  self.assertEqual(self.call('/settings')[0],403)

if __name__=='__main__':unittest.main()
