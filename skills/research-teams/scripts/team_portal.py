#!/usr/bin/env python3
"""Serve a private team dashboard with explicit, shared read receipts."""

from __future__ import annotations

import argparse
import copy
import ctypes
import datetime as dt
import fcntl
import hashlib
import ipaddress
import json
import mimetypes
import os
import secrets
import select
import socket
import struct
import subprocess
import tempfile
import threading
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


def now() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name}: expected a JSON object")
    return value


class TeamStore:
    def __init__(self, source: Path, artifact_roots=(), render_command=()):
        self.source = source.resolve()
        self.lock_path = self.source.with_name(".team-state.lock")
        self.render_command = tuple(render_command)
        self.render_error = None
        self.roots = [self.source.parent, *(Path(p).resolve() for p in artifact_roots)]
        self.lock = threading.RLock()
        self.artifacts: dict[str, Path] = {}
        self.last_good = None

    @staticmethod
    def validate(data: dict) -> dict:
        if type(data.get("schema_version")) is not int or data["schema_version"] != 1:
            raise ValueError("Only schema_version=1 is supported")
        if not isinstance(data.get("team_id"), str) or not data["team_id"]:
            raise ValueError("team_id must be a nonempty string")
        for group in ("tasks", "inbox"):
            values = data.get(group)
            if not isinstance(values, list):
                raise ValueError(f"{group} must be an array")
            ids = []
            for item in values:
                if (
                    not isinstance(item, dict)
                    or not isinstance(item.get("id"), str)
                    or not item["id"]
                ):
                    raise ValueError(f"{group} entries need a nonempty string id")
                ids.append(item["id"])
            if len(set(ids)) != len(ids):
                raise ValueError(f"Duplicate {group} ids")
        for item in data["inbox"]:
            if item.get("read_status", "unread") not in ("read", "unread"):
                raise ValueError("Invalid read_status")
        return data

    def content(self) -> dict:
        return self.validate(read_json(self.source))

    def save(self, data: dict) -> None:
        atomic_write(self.source, json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        self.render_error = None
        if self.render_command:
            try:
                result = subprocess.run(
                    self.render_command,
                    cwd=self.source.parent,
                    capture_output=True,
                    timeout=15,
                    check=False,
                )
                if result.returncode:
                    self.render_error = (
                        "状态已保存，但文档派生失败；请由 lead 检查 renderer。"
                    )
            except (OSError, subprocess.TimeoutExpired):
                self.render_error = (
                    "状态已保存，但文档派生尚未完成；请由 lead 检查 renderer。"
                )

    def publish(self, proposed: dict) -> None:
        proposed = copy.deepcopy(self.validate(proposed))
        with self.lock, self.lock_path.open("a") as lockfile:
            fcntl.flock(lockfile, fcntl.LOCK_EX)
            current = self.content()
            if proposed["team_id"] != current["team_id"]:
                raise ValueError("Publishing cannot change team_id")
            previous = {item["id"]: item for item in current["inbox"]}
            for item in proposed["inbox"]:
                old = previous.get(item["id"])
                if old:
                    for field in (
                        "title",
                        "summary",
                        "significance",
                        "decision_needed",
                        "evidence",
                    ):
                        if item.get(field) != old.get(field):
                            raise ValueError(
                                "Changed inbox content needs a new immutable message id"
                            )
                    for field in ("read_status", "read_updated_at", "read_evidence"):
                        if field in old:
                            item[field] = copy.deepcopy(old[field])
                        else:
                            item.pop(field, None)
                else:
                    item["read_status"] = "unread"
                    item["read_updated_at"] = None
                    item["read_evidence"] = None
            proposed["updated_at"] = now()
            self.save(proposed)

    def allowed_file(self, path: Path) -> bool:
        resolved = path.resolve()
        return resolved.is_file() and any(
            resolved.is_relative_to(root) for root in self.roots
        )

    def normalize_evidence(self, data: dict) -> None:
        artifacts = {}
        for group in ("tasks", "inbox"):
            for item in data[group]:
                evidence = []
                for entry in item.get("evidence", []):
                    if isinstance(entry, str):
                        entry = {"label": entry, "url": entry}
                    if not isinstance(entry, dict):
                        continue
                    label = str(entry.get("label", "证据"))
                    url = str(entry.get("url") or entry.get("path") or "").strip("<>")
                    parsed = urlsplit(url)
                    if parsed.scheme in ("http", "https", "t3-thread"):
                        evidence.append({"label": label, "url": url, "source_url": url})
                    elif url and not parsed.scheme and not url.startswith("//"):
                        path = Path(url)
                        path = (
                            (self.source.parent / path).resolve()
                            if not path.is_absolute()
                            else path.resolve()
                        )
                        if self.allowed_file(path):
                            key = hashlib.sha256(str(path).encode()).hexdigest()[:24]
                            artifacts[key] = path
                            evidence.append(
                                {
                                    "label": label,
                                    "url": f"/artifacts/{key}",
                                    "source_url": str(path),
                                }
                            )
                        else:
                            evidence.append({"label": f"{label} · {url}", "url": None})
                    else:
                        evidence.append({"label": label, "url": None})
                item["evidence"] = evidence
        self.artifacts = artifacts

    def snapshot(self, *, live=False, revision=0) -> dict:
        with self.lock:
            error = None
            try:
                data = self.content()
                for item in data["inbox"]:
                    item.setdefault("read_status", "unread")
                    item["read_changed_at"] = item.get("read_updated_at")
                self.normalize_evidence(data)
                data["_portal"] = {
                    "receipts_updated_at": max(
                        (item.get("read_updated_at") or "" for item in data["inbox"]),
                        default="",
                    )
                    or None
                }
                self.last_good = copy.deepcopy(data)
            except (OSError, ValueError, TypeError, KeyError) as exc:
                if self.last_good is None:
                    raise ValueError(
                        "Coordination data is unavailable or invalid"
                    ) from exc
                data = copy.deepcopy(self.last_good)
                error = "数据暂时无法读取；当前显示最近一次有效内容，请检查协调文件。"
            data["_portal"].update(
                live_updates=live, revision=revision, error=error or self.render_error
            )
            return data

    def set_read(
        self, item_id: str, read: bool, peer: str, source="explicit_web_action"
    ) -> bool:
        if type(read) is not bool or not isinstance(item_id, str):
            raise ValueError("Expected a known id and a JSON boolean read value")
        with self.lock:
            with self.lock_path.open("a") as lockfile:
                fcntl.flock(lockfile, fcntl.LOCK_EX)
                content = self.content()
                item = next(
                    (entry for entry in content["inbox"] if entry["id"] == item_id),
                    None,
                )
                if item is None:
                    raise KeyError("Unknown inbox item")
                status = "read" if read else "unread"
                if item.get("read_status") == status:
                    return False
                changed = now()
                item["read_status"] = status
                item["read_updated_at"] = changed
                item["read_evidence"] = {
                    "source": source,
                    "peer": peer,
                    "human_identity_verified": False,
                }
                content["updated_at"] = changed
                self.save(content)
                return True


class FileEvents:
    """Receive Linux file events, including atomic replacement; never poll files."""

    def __init__(self, paths, callback):
        self.fd = -1
        self.callback = callback
        self.names = {}
        self.thread = None
        self.stop_read, self.stop_write = os.pipe()
        try:
            libc = ctypes.CDLL(None, use_errno=True)
            self.fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
            if self.fd < 0:
                raise OSError(ctypes.get_errno(), "inotify_init1")
            for path in paths:
                path.parent.mkdir(parents=True, exist_ok=True)
                wd = libc.inotify_add_watch(
                    self.fd,
                    os.fsencode(path.parent),
                    0x8 | 0x80 | 0x200 | 0x400 | 0x800,
                )
                if wd < 0:
                    raise OSError(ctypes.get_errno(), "inotify_add_watch")
                self.names.setdefault(wd, set()).add(path.name)
        except (AttributeError, OSError):
            if self.fd >= 0:
                os.close(self.fd)
            self.fd = -1

    @property
    def available(self):
        return self.fd >= 0

    def relevant(self, wd, mask, name):
        return bool(mask & (0x4000 | 0x400 | 0x800 | 0x8000)) or name in self.names.get(
            wd, ()
        )

    def start(self):
        if self.available:
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()

    def run(self):
        while True:
            ready, _, _ = select.select([self.fd, self.stop_read], [], [])
            if self.stop_read in ready:
                return
            payload = os.read(self.fd, 65536)
            offset, changed = 0, False
            while offset + 16 <= len(payload):
                wd, mask, _, length = struct.unpack_from("iIII", payload, offset)
                name = os.fsdecode(
                    payload[offset + 16 : offset + 16 + length].split(b"\0", 1)[0]
                )
                changed |= self.relevant(wd, mask, name)
                offset += 16 + length
            if changed:
                self.callback()

    def close(self):
        os.write(self.stop_write, b"x")
        if self.thread:
            self.thread.join(timeout=2)
        if self.fd >= 0:
            os.close(self.fd)
        os.close(self.stop_read)
        os.close(self.stop_write)


def readable(value) -> str:
    if value is None:
        return "未记录"
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def markdown_views(data: dict) -> dict[str, str]:
    header = f"# {data.get('title', data['team_id'])}\n\n内容更新：{data.get('updated_at', '未记录')}\n\n证据检查：{data.get('evidence_checked_at', '未记录')}\n"
    tasks = [header, "\n## Task List\n"]
    for task in data["tasks"]:
        tasks.append(f"\n### {task['id']} · {task.get('title', '')}\n")
        for field, label in (
            ("question", "问题"),
            ("owner", "Owner"),
            ("status", "状态"),
            ("execution_state", "执行"),
            ("blocker", "阻塞"),
            ("next_action", "下一步"),
            ("acceptance", "验收"),
        ):
            tasks.append(f"\n- {label}：{readable(task.get(field))}\n")
        for entry in task.get("evidence", []):
            tasks.append(
                f"\n- 证据：{entry['label']} · {entry.get('source_url') or entry.get('url') or '见原始记录'}\n"
            )
    inbox = [header, "\n## Human Mailbox\n\n这是共享显式标记状态；已读不等于批准。\n"]
    for item in data["inbox"]:
        inbox.append(f"\n### {item['id']} · {item.get('title', '')}\n")
        for field, label in (
            ("read_status", "阅读状态"),
            ("delivery_status", "投递状态"),
            ("created_at", "时间"),
            ("summary", "结果"),
            ("significance", "意义"),
            ("decision_needed", "待决定"),
        ):
            inbox.append(f"\n- {label}：{readable(item.get(field))}\n")
        for entry in item.get("evidence", []):
            inbox.append(
                f"\n- 证据：{entry['label']} · {entry.get('source_url') or entry.get('url') or '见原始记录'}\n"
            )
    return {"TASKS.md": "".join(tasks), "HUMAN-MAILBOX.md": "".join(inbox)}


class Portal:
    def __init__(self, store: TeamStore, writable=False):
        self.store, self.writable = store, writable
        self.condition = threading.Condition()
        self.revision, self.closed = 0, False
        self.instance_id = secrets.token_urlsafe(12)
        self.token = secrets.token_urlsafe(32)
        self.watcher = FileEvents([store.source], self.changed)
        self.state()  # Watches are registered before the initial snapshot.
        self.watcher.start()

    def state(self):
        data = self.store.snapshot(live=self.watcher.available, revision=self.revision)
        data["_portal"].update(
            instance_id=self.instance_id, csrf_token=self.token, writable=self.writable
        )
        return data

    def changed(self):
        with self.condition:
            self.revision += 1
            self.condition.notify_all()

    def close(self):
        with self.condition:
            self.closed = True
            self.condition.notify_all()
        self.watcher.close()


def handler_for(app: Portal, public_hosts):
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(15)

        def host_valid(self):
            try:
                parsed = urlsplit("http://" + self.headers.get("Host", ""))
                return (
                    parsed.hostname in public_hosts
                    and (parsed.port or 80) == self.server.server_port
                )
            except ValueError:
                return False

        def respond(
            self,
            status,
            body,
            content_type="application/json; charset=utf-8",
            headers=None,
        ):
            payload = body if isinstance(body, bytes) else body.encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            for key, value in (headers or {}).items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(payload)

        def json(self, status, data, headers=None):
            self.respond(status, json.dumps(data, ensure_ascii=False), headers=headers)

        def do_GET(self):
            if not self.host_valid():
                self.json(400, {"error": "Unknown Host"})
                return
            path = urlsplit(self.path).path
            try:
                if path == "/":
                    template = (
                        Path(__file__).resolve().parents[1] / "assets/team-portal.html"
                    )
                    self.respond(
                        200,
                        template.read_text().replace("__CSRF_TOKEN__", app.token),
                        "text/html; charset=utf-8",
                        {
                            "Set-Cookie": f"team_portal={app.token}; HttpOnly; SameSite=Strict; Path=/",
                            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'",
                        },
                    )
                elif path == "/api/state":
                    self.json(
                        200,
                        app.state(),
                        {
                            "Set-Cookie": f"team_portal={app.token}; HttpOnly; SameSite=Strict; Path=/"
                        },
                    )
                elif path == "/api/events":
                    self.events()
                elif path in ("/views/TASKS.md", "/views/HUMAN-MAILBOX.md"):
                    name = path.rsplit("/", 1)[-1]
                    derived = app.store.source.parent / name
                    self.respond(
                        200,
                        derived.read_text()
                        if derived.is_file()
                        else markdown_views(app.state())[name],
                        "text/plain; charset=utf-8",
                    )
                elif path.startswith("/artifacts/"):
                    app.state()
                    target = app.store.artifacts.get(path.rsplit("/", 1)[-1])
                    if target is None or not app.store.allowed_file(target):
                        self.json(404, {"error": "Unknown artifact"})
                    else:
                        kind = (
                            mimetypes.guess_type(target.name)[0]
                            or "application/octet-stream"
                        )
                        self.respond(
                            200,
                            target.read_bytes(),
                            kind,
                            {
                                "Content-Security-Policy": "sandbox; default-src 'none'; img-src data:; style-src 'unsafe-inline'"
                            },
                        )
                else:
                    self.json(404, {"error": "Not found"})
            except (ValueError, OSError):
                self.json(503, {"error": "Coordination data is unavailable or invalid"})

        def events(self):
            if not app.watcher.available:
                self.json(
                    503, {"error": "Live file events unavailable; use manual refresh"}
                )
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()
            revision = -1
            try:
                while not app.closed:
                    with app.condition:
                        app.condition.wait_for(
                            lambda: app.closed or app.revision != revision
                        )
                        if app.closed:
                            return
                        data = app.state()
                        revision = app.revision
                    self.wfile.write(
                        (
                            "event: state\ndata: "
                            + json.dumps(data, ensure_ascii=False)
                            + "\n\n"
                        ).encode()
                    )
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, TimeoutError):
                return

        def do_POST(self):
            if not self.host_valid() or self.headers.get(
                "Origin"
            ) != "http://" + self.headers.get("Host", ""):
                self.json(403, {"error": "Invalid origin"})
                return
            jar = cookies.SimpleCookie()
            try:
                jar.load(self.headers.get("Cookie", ""))
                cookie = jar.get("team_portal")
                valid = cookie is not None and secrets.compare_digest(
                    cookie.value, app.token
                )
            except cookies.CookieError:
                valid = False
            if not valid or not secrets.compare_digest(
                self.headers.get("X-CSRF-Token", ""), app.token
            ):
                self.json(403, {"error": "Refresh the page before changing read state"})
                return
            if self.path != "/api/read-state":
                self.json(404, {"error": "Not found"})
                return
            if not app.writable:
                self.json(
                    403, {"error": "Data owner has not enabled read-state writes"}
                )
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if (
                    not 0 < length <= 8192
                    or self.headers.get_content_type() != "application/json"
                ):
                    raise ValueError("Expected a small JSON request")
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict) or set(data) != {"id", "read"}:
                    raise ValueError("Expected id and read fields")
                changed = app.store.set_read(
                    data["id"], data["read"], self.client_address[0]
                )
                if changed:
                    app.changed()
                self.json(200, app.state())
            except KeyError:
                self.json(404, {"error": "Unknown inbox item"})
            except (ValueError, TypeError):
                self.json(
                    400, {"error": "Expected a known id and a JSON boolean read value"}
                )
            except OSError:
                self.json(503, {"error": "Read state could not be saved"})

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", required=True, type=Path)
    parser.add_argument("--bind", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8841)
    parser.add_argument("--public-host", action="append", default=[])
    parser.add_argument("--artifact-root", type=Path, action="append", default=[])
    parser.add_argument("--allow-read-writes", action="store_true")
    parser.add_argument("--publish", type=Path)
    parser.add_argument("--mark-id")
    parser.add_argument("--read-status", choices=("read", "unread"))
    parser.add_argument("--event-source", default="explicit_human_instruction")
    parser.add_argument("--actor", default="lead")
    parser.add_argument("--render-command", nargs=argparse.REMAINDER, default=[])
    args = parser.parse_args()
    address = ipaddress.IPv4Address(args.bind)
    if not address.is_loopback and address not in ipaddress.IPv4Network(
        "100.64.0.0/10"
    ):
        parser.error("Bind to a loopback or Tailnet IPv4 address")
    store = TeamStore(args.state, args.artifact_root, args.render_command)
    if args.publish:
        store.publish(read_json(args.publish))
        print("Canonical content published with existing read state preserved")
        return
    if args.mark_id:
        if not args.read_status:
            parser.error("--mark-id requires --read-status")
        store.set_read(
            args.mark_id, args.read_status == "read", args.actor, args.event_source
        )
        print("Explicit read-state instruction saved")
        return
    app = Portal(store, args.allow_read_writes)
    server = ThreadingHTTPServer(
        (args.bind, args.port), handler_for(app, {args.bind, *args.public_host})
    )
    try:
        print(f"Team portal: http://{args.bind}:{server.server_port}/", flush=True)
        print(
            "Live file events enabled"
            if app.watcher.available
            else "Manual refresh only",
            flush=True,
        )
        notification = os.environ.get("NOTIFY_SOCKET")
        if notification:
            address = (
                "\0" + notification[1:]
                if notification.startswith("@")
                else notification
            )
            with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as channel:
                channel.connect(address)
                channel.sendall(b"READY=1\nSTATUS=Private team portal ready")
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        app.close()
        server.server_close()


if __name__ == "__main__":
    main()
