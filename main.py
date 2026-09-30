import os
import sys

from dotenv import load_dotenv

load_dotenv()

from convert import write_docs
from pull import grab
from push import sync


def main():
    key = os.environ.get("OPENAI_API_KEY") or os.environ.get("API_KEY")
    if key:
        os.environ["OPENAI_API_KEY"] = key
    limit = int(os.environ.get("LIMIT", "50"))
    articles = grab(limit)
    if len(articles) < 30:
        print("only got %d articles, wanted 30+" % len(articles), file=sys.stderr)
        sys.exit(1)
    docs = write_docs(articles, "docs")
    print("wrote %d markdown files under docs/" % len(docs))
    chunks = sum(d["chunks"] for d in docs)
    print("local_chunk_estimate=%d (split on ##, ~2.6k chars)" % chunks)
    if not (os.environ.get("OPENAI_API_KEY") or os.environ.get("API_KEY")):
        print("no API key, skip upload")
        sys.exit(0)
    sync(docs)
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
