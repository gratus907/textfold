"""A shared server (TEXTFOLD_HOST): each reader's key is used for that reader's own requests and kept nowhere.

    python3 tests/test_shared.py

Starts a server and a stand-in for a model provider that records the key each call arrives with. The server has a
team model (through OLLAMA_MODELS, the same path as the team's OPENROUTER_MODELS). A reader with no key must be
written with the team's; two readers who add a key each must be written with their own, and the text must say whose
account it was. No reply or file may hold a key, and a Claude Code on the server's PATH must be offered to no one and
never run.
"""
import base64
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from textfold import providers

ROOT = Path(__file__).resolve().parent.parent
# a provider's reply to any section: its first paragraph written, the rest left to the author's sentences
REPLY = {"model": "stand-in-served", "choices": [{"message": {"content": json.dumps({
    "section": {"takeaway": "Things hold.", "topic": "holding"},
    "units": [{"id": "U0", "role": "context", "takeaway": "A thing holds.", "topic": "thing", "reason": "It was shown.", "evidence": [0]}]})}}]}
TEXT = "# A title\n\n## One\n\n" + "\n\n".join(f"Paragraph {i} says a thing, and then it says why that thing holds." for i in range(4))


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_shared_server():
    keys_seen = []

    class Provider(BaseHTTPRequestHandler):
        def do_POST(self):
            keys_seen.append(self.headers.get("Authorization"))
            self.rfile.read(int(self.headers.get("Content-Length") or 0))
            reply = json.dumps(REPLY).encode()
            self.send_response(200)
            self.send_header("Content-Length", str(len(reply)))
            self.end_headers()
            self.wfile.write(reply)

        def log_message(self, *args):
            pass

    provider = ThreadingHTTPServer(("127.0.0.1", 0), Provider)
    threading.Thread(target=provider.serve_forever, daemon=True).start()
    port = free_port()
    replies = []

    def call(path, body=None, own=None, origin=None):
        headers = {"Content-Type": "application/json"} | ({"X-Textfold-Settings": own} if own else {}) | ({"Origin": origin} if origin else {})
        req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=None if body is None else json.dumps(body).encode(), headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                status, text, changed = r.status, r.read().decode(), r.headers.get("X-Textfold-Settings")
        except urllib.error.HTTPError as e:
            status, text, changed = e.code, e.read().decode(), None
        replies.append(text)
        return status, json.loads(text), changed

    def written(job, own):
        """Wait for a job to end; the keys the provider saw meanwhile, and whose account the text says it was."""
        before = len(keys_seen)
        for _ in range(240):
            job = next(j for j in call("/api/jobs", own=own)[1] if j["id"] == job["id"])
            if job["status"] not in ("queued", "running"):
                assert job["status"] == "done", job
                layer = json.loads((Path(tmp) / "data" / "papers" / job["pid"] / "layers" / "en.json").read_text())
                return keys_seen[before:], layer["by"], {u.get("model") for u in layer["units"].values()}
            time.sleep(0.25)
        raise AssertionError(f"the job did not end: {job}")

    with tempfile.TemporaryDirectory() as tmp:
        ran = Path(tmp) / "claude-ran"
        fake = Path(tmp) / "bin" / "claude"
        fake.parent.mkdir()
        fake.write_text(f"#!/bin/sh\ntouch {ran}\necho 1.0.0\n")
        fake.chmod(0o755)
        env = {"PATH": f"{fake.parent}{os.pathsep}/usr/bin:/bin", "HOME": tmp, "TEXTFOLD_HOST": "127.0.0.1",
               "TEXTFOLD_DATA": f"{tmp}/data", "PYTHONNOUSERSITE": "1",
               "OLLAMA_MODELS": "team-model", "OLLAMA_BASE_URL": f"http://127.0.0.1:{provider.server_address[1]}"}
        env |= {k: "" for p in providers.ENV_PROVIDERS for k in p["env"]}   # (not the keys in this checkout's .env)
        server = subprocess.Popen([sys.executable, "-m", "textfold", "serve", "--port", str(port)], cwd=ROOT, env=env)
        try:
            for _ in range(100):
                try:
                    socket.create_connection(("127.0.0.1", port), timeout=0.2).close()
                    break
                except OSError:
                    time.sleep(0.1)

            # each reader gives their name and adds a provider: the server answers with their settings and keeps none
            add = {"preset": "custom", "models": ["fold-test-model"], "base": f"http://127.0.0.1:{provider.server_address[1]}"}
            assert call("/api/providers/save", add | {"name": "A", "api_key": "key-A"})[0] == 400   # no name yet
            own = {}
            for who in ("A", "B"):
                own[who] = call("/api/settings", {"name": f"Reader {who}"})[2]
                status, _, own[who] = call("/api/providers/save", add | {"name": who, "api_key": f"key-{who}"}, own=own[who])
                assert status == 200 and f"key-{who}" in base64.b64decode(own[who]).decode()
            team = call("/api/models")[1]
            assert [p["source"] for p in team["providers"]] == ["env"] and team["selected"] == "team-model", team
            mine = call("/api/models", own=own["A"])[1]
            assert [p["name"] for p in mine["providers"]] == ["Ollama", "A"] and mine["providers"][1]["hasKey"] and mine["selected"] == "fold-test-model"
            assert mine["selectedName"].endswith("Reader A's A account"), mine["selectedName"]

            # a text is written with the key of the reader who asked for it, or the team's, and says whose it was
            paper = call("/api/import", {"name": "note.md", "text": TEXT})[1]["paper"]
            for who, key, by in ((None, "ollama", "the team's Ollama account"), ("A", "key-A", "Reader A's A account"), ("B", "key-B", "Reader B's B account")):
                status, job, _ = call("/api/generate", {"paper": paper, "lang": "en", "force": True}, own=own.get(who))
                assert status == 200, job
                used, written_by, wrote = written(job, own.get(who))
                assert used and set(used) == {f"Bearer {key}"} and written_by == by, (who, used, written_by)
                assert wrote == {"stand-in-served", "local"}, wrote   # the model that answered, not the one asked for
            page = urllib.request.urlopen(f"http://127.0.0.1:{port}/p/{paper}", timeout=30).read().decode()
            assert '"written":{' in page and '"stand-in-served":' in page and '"local":' in page   # paragraphs per model
            assert call("/api/generate", {"paper": paper, "lang": "ko"})[0] == 400   # English only

            # the account the server runs under lends nothing: no agent, no bridge, no engine install
            assert not any(a["path"] for a in mine["agents"]) and not any(m["kind"] == "agent" for m in mine["models"])
            assert not call("/api/settings/test", {"model": "claude/claude-code/sonnet"})[1]["ok"]
            assert call("/api/bridge/start", {})[0] == 400 and call("/api/engine/install", {})[0] == 403
            assert not ran.exists()

            # only this server's own pages may write to it
            assert call("/api/jobs/stop", {"id": "none"}, origin="http://evil.example")[0] == 403
            assert call("/api/jobs/stop", {"id": "none"}, origin=f"http://127.0.0.1:{port}")[0] == 404

            # no key in a reply, and none on disk
            assert not any("key-A" in text or "key-B" in text for text in replies)
            assert not (Path(tmp) / ".textfold" / "settings.json").exists()
            held = [f for f in Path(tmp).rglob("*") if f.is_file() and (b"key-A" in f.read_bytes() or b"key-B" in f.read_bytes())]
            assert not held, held
        finally:
            server.terminate()
            server.wait(10)
            provider.shutdown()


if __name__ == "__main__":
    test_shared_server()
    print("ok")
