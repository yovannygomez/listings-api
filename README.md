# listings-api

A small marketplace listings API (FastAPI + pytest). It exists to be worked
on: tickets in Jira describe features, and
[ticket-to-pr](https://github.com/yovannygomez/ticket-to-pr) turns each one
into a spec, tests, code and a pull request.

```bash
pip install -r requirements-dev.txt
pytest -q
uvicorn app.main:app --reload
```

Endpoints: `GET /listings?category=`, `GET /listings/{id}`, `POST /listings`.
Prices are integers in cents.
