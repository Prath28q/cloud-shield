# Test Cases

Run `python -m pytest -q` inside `backend` for the automated smoke tests. Also test these manually through the web interface.

| ID | Input | Expected behavior |
|---|---|---|
| TC01 | `URGENT verify your account now and enter your password http://example.invalid/login` | Elevated risk; urgency, credential, account, and URL indicators appear |
| TC02 | `Our project meeting is tomorrow at 10 AM. Please review the agenda.` | Valid result; usually lower score than TC01, but small ML dataset may cause a nonzero estimate |
| TC03 | URL mode: `http://192.0.2.10/login` | URL IP-address indicator appears |
| TC04 | Empty input | Frontend validation message; API validates too |
| TC05 | More than 5,000 characters | API returns validation error |
| TC06 | GET `/health` | JSON status healthy |
| TC07 | GET `/history` after a scan | Recent records returned while the process stays alive |
| TC08 | Restart backend | In-memory history resets; known limitation |

Record actual output and pass/fail in the final submitted report. Do not report measured accuracy without a labelled test set and metrics.
