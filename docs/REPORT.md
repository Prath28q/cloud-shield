# PhishGuard: Hybrid Rule-Based and Machine-Learning Phishing Message Analyzer

**Lab Mini Project Report**  
**Team size:** 2 members  
**Technology:** React, FastAPI, Python, scikit-learn, Render, Vercel  
**Optional cloud extension:** AWS Lambda, API Gateway, DynamoDB, S3

> Before submission, replace placeholders for student names, USNs, subject, faculty, college, and date. Run the tests and insert genuine screenshots. Do not claim results that you have not measured.

## Abstract
Phishing messages attempt to trick recipients into disclosing credentials, making payments, or visiting deceptive websites. PhishGuard is a proposed educational web application that combines transparent text-pattern rules with a lightweight machine-learning classifier. A React frontend submits a message or URL to a Python API. The backend checks common warning indicators, uses a TF-IDF and logistic-regression pipeline trained on a small synthetic teaching dataset, combines both signals into a risk estimate, and returns an explanation. The project demonstrates a practical web application deployment workflow and illustrates both the benefits and limitations of hybrid detection. It is not intended to replace professional security products.

## 1. Problem Definition
Users can find it difficult to distinguish legitimate messages from phishing attempts that use urgency, account threats, prize claims, suspicious links, or requests for sensitive information. The problem addressed by PhishGuard is to provide an accessible preliminary screening interface that highlights common warning signs and explains why a message may be suspicious. The system must accept message text or a URL, produce a risk estimate, provide understandable reasons, and offer a simple web interface.

## 2. Objectives
- Build a responsive React interface for message and URL analysis.
- Implement explicit rules for common phishing indicators.
- Add a lightweight supervised ML text classifier using TF-IDF and logistic regression.
- Combine rule and ML signals into one risk score.
- Expose the analysis through a REST API.
- Deploy the frontend and backend using beginner-friendly hosting options.
- Test representative inputs and document false-positive, false-negative, privacy, and hosting limitations.

## 3. Proposed System and Architecture
React (Vite) frontend → FastAPI REST API → rule engine + scikit-learn classifier → JSON result. The demonstration backend keeps the latest scan history in memory. The free-hosting version is suitable for a short academic demo, but in-memory history resets when the service restarts and is not a durable database.

### Optional AWS architecture
For an AWS-focused demonstration, the same frontend can be hosted on S3 (preferably behind CloudFront for HTTPS), while API Gateway routes requests to Lambda and DynamoDB stores scan records. The current primary implementation is FastAPI + scikit-learn on Render; the included SAM template from an earlier rule-only version is not the same as this hybrid FastAPI deployment. Do not claim the included hybrid model is running on AWS Lambda unless you port and deploy the model and dependencies there. A production AWS version would need a compatible Lambda package/container and durable history storage.

## 4. Methodology
1. **Input collection:** User pastes a synthetic or non-sensitive message, or a URL.
2. **Validation:** API checks that text is non-empty, no longer than 5,000 characters, and the type is supported.
3. **Rule analysis:** Regular expressions check urgency, credential requests, account threats, links, URL shorteners, prize wording, IP-based URLs, and `@` characters in URLs.
4. **ML analysis:** A TF-IDF vectorizer converts text into numerical features. Logistic regression estimates whether the text resembles the synthetic phishing examples used for training.
5. **Score fusion:** Rule score contributes 65% and ML probability contributes 35%. The final score is mapped to Low (0–29), Medium (30–59), or High (60–100).
6. **Explanation:** Rule matches are listed, alongside the model probability. These explanations are indicators, not proof of maliciousness.
7. **History:** The demo stores up to 50 recent scan records in process memory. A restart clears them. For persistent use, replace this with a database such as DynamoDB or a managed PostgreSQL service.
8. **Deployment:** Host the API on Render and the static React site on Vercel. Configure the frontend environment variable to point to the API.

## 5. Cloud Services and Tools
| Tool/service | Purpose |
|---|---|
| React + Vite | User interface and frontend build |
| Render | Hosts the Python API |
| Vercel | Hosts static React build |
| FastAPI + Uvicorn | REST API and application server |
| scikit-learn | TF-IDF feature extraction and logistic regression |
| GitHub (optional) | Source repository and deployment trigger |
| AWS API Gateway (optional) | Managed HTTP API entry point in an AWS port |
| AWS Lambda (optional) | Serverless execution in an AWS port |
| DynamoDB (optional) | Durable scan history in an AWS port |
| S3 (optional) | Static frontend hosting or object storage |

## 6. Implementation
The project has two main parts:
- `frontend/`: React application, styles, Vite configuration, and deployment environment example.
- `backend/`: FastAPI routes, rule engine, ML pipeline, dependencies, and automated tests.

The model is trained at backend startup using a small synthetic dataset included in `backend/app.py`. This makes setup self-contained but is not a representative real-world dataset. Training and evaluation on a larger, labelled, licensed dataset would be required before drawing meaningful performance conclusions.

## 7. Testing Plan
Run tests from the `backend` directory after installing `requirements-dev.txt` with `python -m pytest -q`.

| ID | Test input / action | Expected result |
|---|---|---|
| T1 | GET `/health` | HTTP 200 and healthy status |
| T2 | Urgent message asking for password and linking to a URL | HTTP 200; elevated score and rule indicators |
| T3 | Benign meeting reminder | HTTP 200; valid score; may still receive a nonzero ML estimate |
| T4 | URL mode with `http://192.0.2.10/login` | HTTP 200; IP-address indicator appears |
| T5 | Empty or whitespace-only text | Validation error (HTTP 422 in FastAPI) |
| T6 | Input longer than 5,000 characters | Validation error |
| T7 | GET `/history` after scans | Recent records returned while same process remains running |
| T8 | Restart free-hosted backend | History clears (known limitation of in-memory storage) |

### Test Results
Record actual results after execution. Suggested table: Test ID | Actual output | Pass/Fail | Screenshot reference. Do not fill every test as Pass until it has been run.

## 8. Results and Discussion
Expected demonstration output includes a risk score, risk band, matched rule explanations, ML probability, and recent scan entries. The combined method can identify some known patterns while offering a model-based signal for text that does not match an explicit rule. The score is heuristic and is not a calibrated probability of compromise. The synthetic training dataset is intentionally small and may generalize poorly. False positives and false negatives are expected. Actual accuracy, precision, recall, F1 score, and confusion matrix must be measured on a separate labelled test dataset if the project is extended into a formal ML evaluation.

## 9. Security, Privacy, and Cost Limitations
- Never paste actual passwords, OTPs, bank details, confidential correspondence, or private URLs.
- Do not fetch or open submitted URLs; this project analyzes text patterns only.
- The demo has no user authentication, abuse prevention, or rate limiting.
- The API returns only a short preview in history, but previews can still expose sensitive content. Use synthetic data and add redaction or avoid storing previews for any real use.
- CORS configured as `*` is convenient for a student demo, not an access-control mechanism. Set `FRONTEND_ORIGIN` to the exact deployed frontend origin before a public demo.
- Render free services may sleep or have usage limits; cold starts can delay requests. Free plan terms change, so verify current availability.
- Vercel and Render free tiers have quotas and fair-use restrictions. External traffic, build minutes, bandwidth, or upgraded features may incur charges.
- AWS is not automatically free. API Gateway, Lambda, DynamoDB, S3, CloudFront, logs, and data transfer have quotas and pricing. Enable billing alerts and remove resources after evaluation.
- ML training data is small and synthetic. This prototype must not be used as a production security decision system.

## 10. Future Enhancements
- Train and evaluate on a larger, ethically sourced labelled dataset.
- Report precision, recall, F1 score, and confusion matrix.
- Add user authentication, per-user history, rate limiting, and input redaction.
- Use persistent storage such as DynamoDB or managed PostgreSQL.
- Add trusted URL reputation feeds without automatically visiting suspicious links.
- Port the model to AWS Lambda using a compatible deployment package or container image.
- Add model versioning and threshold calibration.

## 11. Conclusion
PhishGuard demonstrates a hybrid approach to phishing-awareness screening by combining explicit rule-based indicators with a lightweight machine-learning text classifier. Its React interface and REST API provide a clear example of frontend/backend separation and cloud deployment. The prototype helps explain suspicious patterns but cannot guarantee detection. The small synthetic training set, lack of authentication, and non-persistent free-host history limit it to controlled educational demonstrations. Larger-scale evaluation, secure storage, access controls, and monitoring would be necessary for a practical deployment.

## References
1. React documentation: https://react.dev/
2. FastAPI documentation: https://fastapi.tiangolo.com/
3. scikit-learn documentation: https://scikit-learn.org/stable/
4. Render documentation: https://render.com/docs
5. Vercel documentation: https://vercel.com/docs
6. AWS Lambda documentation: https://docs.aws.amazon.com/lambda/
7. Amazon API Gateway documentation: https://docs.aws.amazon.com/apigateway/
8. Amazon DynamoDB documentation: https://docs.aws.amazon.com/dynamodb/
