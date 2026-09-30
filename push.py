import json
import os
import time

from openai import OpenAI

STATE = "run_state.json"


def _client():
    key = os.environ.get("OPENAI_API_KEY") or os.environ.get("API_KEY")
    if not key:
        raise SystemExit("need OPENAI_API_KEY or API_KEY")
    return OpenAI(api_key=key)


def _vs(client):
    if hasattr(client, "vector_stores"):
        return client.vector_stores
    return client.beta.vector_stores


def load_state():
    if not os.path.exists(STATE):
        return {"vector_store_id": os.environ.get("VECTOR_STORE_ID") or "", "items": {}}
    with open(STATE, encoding="utf-8") as f:
        data = json.load(f)
    env_id = os.environ.get("VECTOR_STORE_ID") or ""
    if env_id:
        data["vector_store_id"] = env_id
    data.setdefault("items", {})
    return data


def save_state(data):
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    os.replace(tmp, STATE)


def ensure_store(client, data):
    api = _vs(client)
    vs_id = (data.get("vector_store_id") or "").strip()
    if vs_id:
        try:
            api.retrieve(vs_id)
            return vs_id
        except Exception:
            print("stored vector id is dead, making a new one")
    store = api.create(name="help-md")
    data["vector_store_id"] = store.id
    save_state(data)
    print("vector_store_id=%s" % store.id)
    return store.id


def _drop(client, vs_id, file_id):
    api = _vs(client)
    if not file_id:
        return
    try:
        api.files.delete(vector_store_id=vs_id, file_id=file_id)
    except Exception:
        pass
    try:
        client.files.delete(file_id)
    except Exception:
        pass


def _put(client, vs_id, path, name):
    api = _vs(client)
    with open(path, "rb") as f:
        fobj = client.files.create(file=(name, f), purpose="assistants")
    kw = dict(
        vector_store_id=vs_id,
        file_id=fobj.id,
        chunking_strategy={
            "type": "static",
            "static": {"max_chunk_size_tokens": 800, "chunk_overlap_tokens": 200},
        },
    )
    try:
        api.files.create_and_poll(**kw)
    except TypeError:
        kw.pop("chunking_strategy", None)
        api.files.create_and_poll(**kw)
    return fobj.id


def sync(docs):
    client = _client()
    data = load_state()
    vs_id = ensure_store(client, data)
    prev = data.get("items") or {}
    added = updated = skipped = 0
    chunks_added = 0
    seen = set()

    for row in docs:
        aid = row["id"]
        seen.add(aid)
        old = prev.get(aid) or {}
        if old.get("hash") == row["hash"] and old.get("file_id"):
            skipped += 1
            continue
        if old.get("file_id"):
            _drop(client, vs_id, old["file_id"])
            updated += 1
        else:
            added += 1
        fid = _put(client, vs_id, row["path"], row["name"])
        prev[aid] = {
            "hash": row["hash"],
            "file_id": fid,
            "name": row["name"],
            "updated": row["updated"],
        }
        chunks_added += row["chunks"]
        time.sleep(0.25)

    gone = [k for k in list(prev) if k not in seen]
    for k in gone:
        _drop(client, vs_id, (prev[k] or {}).get("file_id"))
        prev.pop(k, None)

    data["items"] = prev
    data["vector_store_id"] = vs_id
    save_state(data)
    print(
        "added=%d updated=%d skipped=%d dropped=%d files=%d chunks=%d"
        % (added, updated, skipped, len(gone), len(docs), chunks_added)
    )
    print("embedded_this_run files=%d chunks=%d" % (added + updated, chunks_added))
    print("vector_store_id=%s" % vs_id)
    return vs_id
