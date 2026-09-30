# cedar-splice

Daily ingest for a small support assistant. Pulls Help Center articles, writes markdown, then uploads only what changed into an OpenAI vector store.

## setup

Python 3.11+, an OpenAI key with a few dollars of credit.

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.sample .env
```

Put the key in `.env` as `OPENAI_API_KEY`. `API_KEY` works too (that's what the docker one-liner uses). After the first successful upload, copy `vector_store_id=...` from the log into `.env` as `VECTOR_STORE_ID` so reruns hit the same store.

## run locally

```
python main.py
```

It grabs ≥30 articles from the Zendesk Help Center API (no nav/chrome), writes `docs/*.md`, then uploads the delta. Logs look like `added= / updated= / skipped=`. Chunking: we split on `##` at ~2.6k chars just to log a count; OpenAI actually embeds with static chunks of 800 tokens / 200 overlap.

First run prints `vector_store_id=vs_...`. In the OpenAI Playground, create an Assistant, paste the system prompt from the brief, turn on file search, attach that vector store. Ask: **How do I add a YouTube video?** Screenshot goes here: `shot.png`.

## docker

```
docker build -t cedar-splice .
docker run --rm -e API_KEY=$OPENAI_API_KEY cedar-splice
```

One shot, then it exits 0.

## daily job logs

GitHub Actions workflow `.github/workflows/daily.yml` (cron + manual). After you push and add secrets `OPENAI_API_KEY` and `VECTOR_STORE_ID`, the run log is:

https://github.com/<you>/cedar-splice/actions

Latest artefact is `last-run` on that workflow.

## chunking (short)

One `.md` file per article. Heading split is only for the log line. The store uses OpenAI static chunking (800 / 200). Each file starts with `Article URL:` so answers can cite it.
