from fastapi.testclient import TestClient
from app import app
client=TestClient(app)
def test_health(): assert client.get('/health').json()['status']=='healthy'
def test_phishy_message():
 r=client.post('/analyze',json={'type':'message','text':'URGENT verify your account now and enter your password http://example.invalid/login'})
 assert r.status_code==200 and r.json()['score']>=30 and r.json()['level'] in ['Medium','High']
def test_benign_message():
 r=client.post('/analyze',json={'type':'message','text':'Our project meeting is tomorrow at 10 AM. Please review the agenda.'})
 assert r.status_code==200 and 0<=r.json()['score']<=100
def test_empty_rejected(): assert client.post('/analyze',json={'type':'message','text':' '}).status_code==422
def test_url_mode(): assert client.post('/analyze',json={'type':'url','text':'http://192.0.2.10/login'}).status_code==200
