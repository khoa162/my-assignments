import hashlib
import os
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from markdownify import markdownify as tomd

HOST = "https://support.optisigns.com"
DROP = (
    "leader in digital signage",
    "feel free to reach out to our support team",
    "if you have any additional questions, concerns or any feedback",
)


def _slug(url, title, aid):
    if url and "/articles/" in url:
        tail = url.rstrip("/").split("/articles/")[-1]
        tail = tail.split("?")[0]
        if tail:
            return tail[:120]
    s = re.sub(r"[^a-z0-9]+", "-", (title or "").lower()).strip("-")
    return "%s-%s" % (aid, s[:80] or "article")


def _abs(href):
    if not href:
        return href
    href = href.strip()
    if href.startswith("#") or href.startswith("mailto:") or href.startswith("data:"):
        return href
    return urljoin(HOST, href)


def _clean_html(raw):
    soup = BeautifulSoup(raw or "", "lxml")
    for tag in soup.find_all(["script", "style", "nav", "footer", "iframe"]):
        tag.decompose()
    for img in soup.find_all("img"):
        src = img.get("src")
        if src:
            img["src"] = _abs(src)
        if img.get("alt") is None:
            img["alt"] = ""
    for a in soup.find_all("a"):
        href = a.get("href")
        if href:
            a["href"] = _abs(href)
    for p in list(soup.find_all("p")):
        txt = (p.get_text() or "").lower()
        if any(bit in txt for bit in DROP):
            p.decompose()
    return str(soup)


def to_markdown(article):
    title = (article.get("title") or "Untitled").strip()
    url = article.get("html_url") or ""
    html = _clean_html(article.get("body") or "")
    md = tomd(html, heading_style="ATX", bullets="-", code_language="")
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    md = md.replace("\xa0", " ")
    bits = [
        "# %s" % title,
        "",
        "Article URL: %s" % url,
        "Last-Modified: %s" % (article.get("edited_at") or article.get("updated_at") or ""),
        "",
        md,
        "",
    ]
    return "\n".join(bits)


def fingerprint(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def chunk_count(text):
    parts = re.split(r"\n(?=## )", text)
    chunks = []
    buf = ""
    for p in parts:
        if buf and len(buf) + len(p) > 2600:
            chunks.append(buf)
            buf = p
        else:
            buf = p if not buf else buf + "\n" + p
    if buf:
        chunks.append(buf)
    return max(len(chunks), 1)


def write_docs(articles, folder="docs"):
    os.makedirs(folder, exist_ok=True)
    out = []
    for a in articles:
        aid = str(a["id"])
        name = _slug(a.get("html_url"), a.get("title"), aid) + ".md"
        path = os.path.join(folder, name)
        body = to_markdown(a)
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)
        out.append(
            {
                "id": aid,
                "path": path,
                "name": name,
                "hash": fingerprint(body),
                "chunks": chunk_count(body),
                "updated": a.get("edited_at") or a.get("updated_at") or "",
            }
        )
    return out
