"""A text folded on a reader's own computer, published to the team's server (TEXTFOLD_HOST).

  python3 -m textfold publish <paper> --to http://<the team's server>:3017 [--as <your name>]

The reader folds with their own agent or key (Claude Code, Codex, an API key), so their sign-in never leaves their
computer. What goes to the team is the text and what the model wrote about it, as words: each paragraph's role,
takeaway, reason, topic and key sentences, each section's takeaway and topic, and the argument links. Notes, questions
and the model's replies stay home.

The server takes none of it as it came. The text: an arXiv paper is fetched from arXiv; any other is the HTML the
reader's TextFold stored (semantic.normalize), made safe again (semantic.sanitize), with its pictures (PNG, JPEG, GIF,
WebP). A text the server already has stays as it is. Either way it must read as the reader's did (the same sections,
paragraphs and words: fingerprint), or nothing is kept. The levels are written again from the words by the server's own
code, as from a model's reply (ladder.assemble), and links are kept only between paragraphs that exist.
"""
import base64
import hashlib
import json
import re
import shutil
import urllib.request

from . import fetch, ladder, links, local, semantic, store
from .parse import parse
from .tokens import plain

LIMIT = 2000   # a written line's characters (a takeaway is about 14 words, a reason 22)
META = ("title", "date", "version", "snapshot", "label", "doi")   # a meta.json's fields of text (links: meta_of)


def fingerprint(doc):
    """What two parses of one text share when they read it alike: its sections, and its paragraphs' words."""
    return hashlib.sha256(json.dumps([[[c["id"], c["units"]] for c in doc["chunks"]],
                                      [[uid, plain(u["toks"], doc["atoms"])] for uid, u in doc["units"].items()]]).encode()).hexdigest()


def words(doc, en):
    """A stored layer (en.json) as the words the model wrote, what layer() writes as levels again."""
    A = doc["atoms"]
    units = {uid: {"role": lad["role"], "evidence": lad["ev"], "takeaway": plain(lad["brief"][:lad["tn"]], A),
                   "reason": plain(lad["brief"][lad["tn"] + 1:-1], A), "topic": plain(lad["topic"], A), "model": lad["model"]}
             for uid, lad in en["units"].items() if lad["model"] != "local"}
    chunks = {cid: {"takeaway": plain(lad["take"], A), "topic": plain([lad["take"][i] for i in lad["topic"]], A)}
              for cid, lad in en["chunks"].items() if lad}
    return {"model": en["model"], "units": units, "chunks": chunks, "edges": en["edges"]}


def _text(v):
    return v[:LIMIT] if isinstance(v, str) else ""


def layer(doc, w, by):
    """The words published, written as levels by this server's code: the en layer (store.save_en's shape)."""
    try:
        said = w.get("chunks") or {}
        units = {uid: ladder.assemble(doc["units"][uid], {"role": o.get("role"), "evidence": o.get("evidence") if isinstance(o.get("evidence"), list) else [],
                                                          **{k: _text(o.get(k)) for k in ("takeaway", "reason", "topic")}},
                                      doc["atoms"], _text(o.get("model"))[:100] or "unknown")
                 for uid, o in (w.get("units") or {}).items() if uid in doc["units"] and isinstance(o, dict)}
        chunks = {c["id"]: ladder.section_ladder({"takeaway": _text(said[c["id"]].get("takeaway")), "topic": _text(said[c["id"]].get("topic"))}, 3, doc, c)
                  for c in doc["chunks"] if c["units"] and isinstance(said.get(c["id"]), dict)}
        edges = [{"f": e["f"], "t": e["t"], "tk": "unit", "rel": e["rel"]} for e in w.get("edges") or []
                 if isinstance(e, dict) and all(isinstance(e.get(k), str) for k in ("f", "t", "rel"))
                 and e["f"] in doc["units"] and e["t"] in doc["units"] and e["rel"] in links.RELS]
    except (AttributeError, TypeError) as e:   # not the words of a layer
        raise ValueError(f"not a TextFold layer ({e})") from None
    return {"version": store.stamp(), "model": _text(w.get("model"))[:100], "by": by,
            "units": units, "chunks": {c["id"]: chunks.get(c["id"]) for c in doc["chunks"]}, "edges": edges}


def _link(v):
    """A link a page may follow: one to the web (a javascript: link would run on this server's pages)."""
    return v if isinstance(v, str) and re.match(r"https?://", v, re.I) else ""


def meta_of(m, pid):
    """A published text's meta.json: the fields a page shows, as text, and its links only to the web."""
    src = m.get("source") if isinstance(m.get("source"), dict) else {}
    return {**{k: m[k][:500] for k in META if isinstance(m.get(k), str)}, "id": pid,
            "title": m["title"][:500] if isinstance(m.get("title"), str) and m["title"].strip() else pid,
            "authors": [a[:200] for a in m["authors"] if isinstance(a, str)][:100] if isinstance(m.get("authors"), list) else [],
            "abs_url": _link(m.get("abs_url")), "html_url": _link(m.get("html_url")), "license": _link(m.get("license")),
            "source": {k: v[:500] for k, v in src.items() if isinstance(v, str) and k != "url"} | ({"url": _link(src["url"])} if "url" in src else {})}


def pictures(img):
    """name -> bytes: the pictures that are pictures (PNG, JPEG, GIF, WebP, by their first bytes), under plain names."""
    out = {}
    for name, b64 in (img or {}).items():
        data = base64.b64decode(b64) if isinstance(b64, str) else b""
        if (re.fullmatch(r"[\w][\w.-]{0,99}", name) and len(data) <= local.MAX_IMG and (data[:4] in (b"\x89PNG", b"GIF8")
                                                                                        or data[:3] == b"\xff\xd8\xff" or data[:4] + data[8:12] == b"RIFFWEBP")):
            out[name] = data
    return out


def receive(body):
    """Keep a published text (ValueError: why not). Returns its id, title, and how many of its paragraphs have levels."""
    pid = body.get("paper")
    if not (isinstance(pid, str) and store.valid_id(pid)):
        raise ValueError("not a paper's id")
    d = store.pdir(pid)
    stored = (d / "meta.json").exists() and (d / "source.html").exists()
    if store.ARXIV_ID.fullmatch(pid):   # its source is arXiv's, never the one sent
        fetch.fetch(pid, store.DATA)
        stored = True
    if stored:
        doc = store.parsed(pid)
    else:
        img = pictures(body.get("img"))
        meta = meta_of(body.get("meta") if isinstance(body.get("meta"), dict) else {}, pid)
        html = semantic.sanitize(body["source"] if isinstance(body.get("source"), str) else "", {f"img/{n}" for n in img})
        doc = parse(html, dict(meta))
    if fingerprint(doc) != body.get("fingerprint"):
        raise ValueError("The team's copy of this text reads differently from yours (another version of the text, or of "
                         "TextFold): nothing was kept")
    name = _text(body.get("name")).strip()[:60]
    en = layer(doc, body.get("words") if isinstance(body.get("words"), dict) else {}, f"{name or 'an unnamed reader'}'s account")
    placed = sum(lad["model"] != "local" for lad in en["units"].values())
    if not placed:
        raise ValueError("nothing written to publish: fold it first")
    if not stored:   # written whole or not at all, as local.store_doc writes
        tmp = d.with_name(d.name + ".tmp")
        shutil.rmtree(tmp, ignore_errors=True)
        (tmp / "img").mkdir(parents=True)
        try:
            for n, data in img.items():
                (tmp / "img" / n).write_bytes(data)
            (tmp / "source.html").write_text(html)
            (tmp / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
            shutil.rmtree(d, ignore_errors=True)
            tmp.rename(d)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    store.write(pid, "en", en)
    return {"paper": pid, "title": doc["meta"]["title"], "placed": placed, "of": len(doc["units"])}


def send(ref, to, name):
    """Publish a folded text from this computer to the team's server at `to` (its reply; urllib.error.HTTPError: refused).
    ref: its id, its link, or its address in the reader (http://localhost:3017/p/<id>)."""
    m = re.search(r"/p/([\w.-]+)", ref)
    pid = m.group(1) if m and store.valid_id(m.group(1)) else store.resolve(ref)
    en = store.read(pid, "en")
    if not en:
        raise ValueError(f"{pid} has no levels yet: fold it first (python3 -m textfold get {pid})")
    doc = store.parsed(pid)
    body = {"paper": pid, "name": name, "fingerprint": fingerprint(doc), "words": words(doc, en)}
    if not store.ARXIV_ID.fullmatch(pid):
        d = store.pdir(pid)
        body |= {"meta": json.loads((d / "meta.json").read_text()), "source": (d / "source.html").read_text(),
                 "img": {f.name: base64.b64encode(f.read_bytes()).decode() for f in sorted((d / "img").glob("*")) if f.is_file()}}
    req = urllib.request.Request(f"{to.rstrip('/')}/api/publish", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())
