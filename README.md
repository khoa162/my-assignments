# my-assignments

Daily ingest for a small support assistant. Pulls Help Center articles, writes markdown, then uploads only what changed into an OpenAI vector store.

## setup

Python 3.11+, an OpenAI key with a few dollars of credit.

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.sample .env
```

Put the key in `.env` as `OPENAI_API_KEY`. `API_KEY` works too for Docker (`docker run -e API_KEY=...`). After the first upload, set `VECTOR_STORE_ID` from the log so later runs reuse the same store.

## run locally

```
python main.py
```

Pulls ≥30 articles from the Zendesk Help Center API, writes `docs/*.md`, uploads the delta. Logs: `added=` / `updated=` / `skipped=`. Local chunk estimate splits on `##` (~2.6k chars); OpenAI embeds with static chunks 800 / 200 overlap.

In the OpenAI Playground (Chat), paste the OptiBot system prompt from the brief, enable **File search**, attach vector store `help-md`, ask **How do I add a YouTube video?**

Screenshot: [`screenshots/Screenshot 2026-09-30 at 21.41.26.png`](screenshots/Screenshot%202026-09-30%20at%2021.41.26.png)

## docker

```
docker build -t my-assignments .
docker run --rm -e API_KEY=$OPENAI_API_KEY my-assignments
```

One shot, then exits 0.

## daily job logs

GitHub Actions: `.github/workflows/daily.yml` (cron + manual).

Latest successful run (manual):

https://github.com/khoa162/my-assignments/actions/runs/36735279940

Workflow list: https://github.com/khoa162/my-assignments/actions/workflows/daily.yml

Artefact on that run: `last-run`.

## chunking (short)

One `.md` per article. Heading split is only for the log line. Store uses OpenAI static chunking (800 / 200). Files start with `Article URL:` for citations.

## planning (part 2)

See [`PLAN.md`](PLAN.md).
