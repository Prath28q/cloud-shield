import os, re, uuid
from datetime import datetime, timezone
from typing import Literal
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# Small, synthetic teaching dataset. This is a demonstration classifier, not a production model.
TRAINING_TEXTS = [
 "team meeting moved to tomorrow please review the attached agenda",
 "thank you for your order your package will arrive on Friday",
 "your class assignment is available on the college portal",
 "hello can we reschedule our project discussion to next week",
 "monthly newsletter with updates and community events",
 "your appointment is confirmed for 10 am tomorrow",
 "URGENT verify your account now or it will be suspended click this link",
 "your bank account is blocked enter your password and OTP immediately",
 "you won a free prize claim your reward now by clicking here",
 "security alert confirm your card details immediately to avoid closure",
 "final warning update your login password at this unfamiliar link",
 "pay the fee now or your account will be deleted provide bank details",
 "click here to claim your free gift within 24 hours",
 "unusual activity detected sign in now and provide your passcode",
 "invoice attached please review the document when you have time",
 "your password reset request was received if this was not you contact support",
 "congratulations you have won a prize send your credit card details",
 "dear student your exam timetable is published on the official portal",
 "urgent payment required immediately verify account and enter one time code",
 "the library will remain closed on Sunday thanks for your cooperation",
]
TRAINING_LABELS = [0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,1,0,1,0]
model = Pipeline([("tfidf", TfidfVectorizer(ngram_range=(1,2), lowercase=True, sublinear_tf=True)), ("clf", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=7))])
model.fit(TRAINING_TEXTS, TRAINING_LABELS)

RULES = [
 (re.compile(r'\b(urgent|immediately|act now|final warning|within 24 hours|limited time)\b', re.I), 18, 'Urgent or pressure-based wording'),
 (re.compile(r'\b(password|passcode|one[- ]time code|\botp\b|pin number|bank details|credit card|social security number)\b', re.I), 24, 'Mentions sensitive credentials or financial information'),
 (re.compile(r'\b(account (?:will be|has been) (?:blocked|suspended|closed)|verify your account|unusual activity detected)\b', re.I), 18, 'Account-threat or verification language'),
 (re.compile(r'\b(click here|click the link|open this link|confirm now|sign in now)\b', re.I), 12, 'Encourages the recipient to click or act'),
 (re.compile(r'https?://[^\s<>\"]+', re.I), 8, 'Contains a web link'),
 (re.compile(r'(?:bit\.ly|tinyurl\.com|t\.co|is\.gd|cutt\.ly)/', re.I), 15, 'Uses a URL-shortening service'),
 (re.compile(r'\b(prize|you have won|claim your reward|free gift)\b', re.I), 12, 'Prize or reward wording may be used as bait'),
]
app=FastAPI(title='PhishGuard API', version='1.0.0', description='Educational hybrid phishing-indicator analyzer')
origins=[x.strip() for x in os.getenv('FRONTEND_ORIGIN','*').split(',') if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=['GET','POST','OPTIONS'], allow_headers=['Content-Type'])
# In-memory history is deliberately simple for the lab. It resets when the free host restarts.
history=[]
class ScanRequest(BaseModel):
 text: str = Field(min_length=1, max_length=5000)
 type: Literal['message','url'] = 'message'

def analyze(text: str, kind: str):
 score=0; reasons=[]
 for pattern, points, reason in RULES:
  if pattern.search(text): score+=points; reasons.append(reason)
 if kind=='url':
  if not re.match(r'^https?://', text, re.I): score+=12; reasons.append('URL does not begin with HTTP or HTTPS')
  if '@' in text: score+=18; reasons.append('URL contains an @ symbol that may obscure the destination')
  if re.search(r'https?://\d{1,3}(?:\.\d{1,3}){3}',text,re.I): score+=18; reasons.append('URL uses an IP address instead of a domain name')
  host=re.search(r'^https?://([^/?:#]+)',text,re.I)
  if host and host.group(1).count('-')>=3: score+=8; reasons.append('Hostname contains multiple hyphens')
 rule_score=min(100,score)
 ml_probability=float(model.predict_proba([text])[0][1])
 ml_score=round(ml_probability*100)
 # Combine interpretable rule score and model probability: 65% rules, 35% ML.
 final_score=round(min(100, max(0, 0.65*rule_score+0.35*ml_score)))
 if not reasons: reasons=['No configured rule warning patterns were detected']
 reasons.append(f'ML text classifier estimated {ml_score}% phishing-like probability (small teaching dataset)')
 level='High' if final_score>=60 else 'Medium' if final_score>=30 else 'Low'
 return final_score,level,reasons,rule_score,ml_score

@app.get('/')
def root(): return {'name':'PhishGuard API','status':'ok','docs':'/docs'}
@app.get('/health')
def health(): return {'status':'healthy'}
@app.post('/analyze')
def scan(req: ScanRequest):
 text=req.text.strip()
 if not text: raise HTTPException(status_code=400,detail='Enter a message or URL to analyze.')
 score,level,reasons,rule_score,ml_score=analyze(text,req.type)
 item={'id':str(uuid.uuid4()),'score':score,'level':level,'reasons':reasons,'type':req.type,'createdAt':datetime.now(timezone.utc).isoformat(),'preview':text[:80],'ruleScore':rule_score,'mlScore':ml_score}
 history.insert(0,item); del history[50:]
 return item
@app.get('/history')
def get_history(limit:int=10): return {'items':history[:max(1,min(limit,50))]}
