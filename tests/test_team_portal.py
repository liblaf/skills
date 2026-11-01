"""Behavior checks use disposable inboxes, never actual human read state."""

import copy
import http.client
import importlib.util
import json
import tempfile
import threading
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1] / "skills/research-teams/scripts/team_portal.py"
)
SPEC = importlib.util.spec_from_file_location("team_portal", SCRIPT)
portal = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(portal)


class PortalBehavior(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.source = self.root / "team-state.json"
        self.data = {
            "schema_version": 1,
            "team_id": "fixture",
            "title": "Fixture",
            "updated_at": "2026-11-01T12:00:00Z",
            "evidence_checked_at": "2026-10-31T12:00:00Z",
            "tasks": [
                {
                    "id": "T-1",
                    "title": "Unfinished scientific question",
                    "status": "in_progress",
                    "blocker": "license",
                    "evidence": [],
                }
            ],
            "inbox": [
                {
                    "id": "fixture:H-1",
                    "title": "<script>untrusted()</script>",
                    "summary": "Result",
                    "decision_needed": "Pending",
                    "delivery_status": "presented",
                    "evidence": [],
                }
            ],
        }
        portal.atomic_write(self.source, json.dumps(self.data))
        self.store = portal.TeamStore(self.source)
        self.app = portal.Portal(self.store, writable=True)
        self.server = portal.ThreadingHTTPServer(
            ("127.0.0.1", 0), portal.handler_for(self.app, {"127.0.0.1"})
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.app.close()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temporary.cleanup()

    def request(
        self,
        method="GET",
        path="/api/state",
        data=None,
        authenticated=False,
        origin=None,
    ):
        connection = http.client.HTTPConnection(
            "127.0.0.1", self.server.server_port, timeout=3
        )
        headers = {}
        if authenticated:
            headers = {
                "Origin": origin or f"http://127.0.0.1:{self.server.server_port}",
                "Cookie": f"team_portal={self.app.token}",
                "X-CSRF-Token": self.app.token,
                "Content-Type": "application/json",
            }
        connection.request(
            method, path, json.dumps(data) if data is not None else None, headers
        )
        response = connection.getresponse()
        status, payload = response.status, response.read()
        connection.close()
        return status, payload

    def test_viewing_and_delivery_never_mark_read_or_approve(self):
        for path in ("/", "/api/state", "/views/HUMAN-MAILBOX.md"):
            self.assertEqual(self.request(path=path)[0], 200)
        self.assertEqual(json.loads(self.source.read_text()), self.data)
        state = self.store.snapshot()
        self.assertEqual(state["inbox"][0]["read_status"], "unread")
        self.assertEqual(state["inbox"][0]["decision_needed"], "Pending")
        self.assertEqual(state["evidence_checked_at"], self.data["evidence_checked_at"])
        self.assertEqual(json.loads(self.source.read_text()), self.data)

    def test_explicit_idempotent_read_unread_survives_content_update_and_restart(self):
        action = {"id": "fixture:H-1", "read": True}
        self.assertEqual(self.request("POST", "/api/read-state", action, True)[0], 200)
        first_receipt = self.source.read_bytes()
        self.assertEqual(self.request("POST", "/api/read-state", action, True)[0], 200)
        self.assertEqual(self.source.read_bytes(), first_receipt)
        updated = copy.deepcopy(self.data)
        updated["tasks"][0]["next_action"] = "Wait for the actual license event"
        self.store.publish(updated)
        reopened = portal.TeamStore(self.source)
        self.assertEqual(reopened.snapshot()["inbox"][0]["read_status"], "read")
        self.assertEqual(
            reopened.snapshot()["tasks"][0]["next_action"],
            updated["tasks"][0]["next_action"],
        )
        self.assertEqual(
            self.request(
                "POST", "/api/read-state", {"id": "fixture:H-1", "read": False}, True
            )[0],
            200,
        )
        self.assertEqual(self.store.snapshot()["inbox"][0]["read_status"], "unread")
        final = json.loads(self.source.read_text())
        self.assertEqual(final["tasks"], updated["tasks"])
        self.assertEqual(final["inbox"][0]["decision_needed"], "Pending")

    def test_mutation_rejects_cross_origin_unknown_ids_and_non_boolean(self):
        for authenticated, origin, action, expected in (
            (False, None, {"id": "fixture:H-1", "read": True}, 403),
            (True, "http://attacker.invalid", {"id": "fixture:H-1", "read": True}, 403),
            (True, None, {"id": "other:H-1", "read": True}, 404),
            (True, None, {"id": "fixture:H-1", "read": "true"}, 400),
            (
                True,
                None,
                {"id": "fixture:H-1", "read": True, "decision_needed": "Approved"},
                400,
            ),
        ):
            status, _ = self.request(
                "POST", "/api/read-state", action, authenticated, origin
            )
            self.assertEqual(status, expected)
        self.assertEqual(json.loads(self.source.read_text()), self.data)

    def test_invalid_state_preserves_last_good_and_rejects_mutations(self):
        self.store.snapshot()
        portal.atomic_write(self.source, "{")
        state = self.store.snapshot()
        self.assertIsNotNone(state["_portal"]["error"])
        self.assertEqual(state["tasks"][0]["blocker"], "license")
        self.assertEqual(
            self.request(
                "POST", "/api/read-state", {"id": "fixture:H-1", "read": True}, True
            )[0],
            400,
        )
        self.assertEqual(self.source.read_text(), "{")

    def test_incompatible_schema_preserves_last_good_snapshot(self):
        self.store.snapshot()
        incompatible = copy.deepcopy(self.data)
        incompatible["schema_version"] = 2
        portal.atomic_write(self.source, json.dumps(incompatible))
        result = self.store.snapshot()
        self.assertEqual(result["schema_version"], 1)
        self.assertIsNotNone(result["_portal"]["error"])

    def test_restart_state_includes_new_incarnation_and_renewed_csrf(self):
        first = self.app.state()
        other = portal.Portal(portal.TeamStore(self.source), writable=True)
        try:
            current = other.state()
            self.assertNotEqual(
                first["_portal"]["instance_id"], current["_portal"]["instance_id"]
            )
            self.assertNotEqual(
                first["_portal"]["csrf_token"], current["_portal"]["csrf_token"]
            )
            connection = http.client.HTTPConnection(
                "127.0.0.1", self.server.server_port, timeout=3
            )
            connection.request("GET", "/api/state")
            response = connection.getresponse()
            cookie = response.getheader("Set-Cookie")
            body = json.loads(response.read())
            self.assertIn(body["_portal"]["csrf_token"], cookie)
            connection.close()
        finally:
            other.close()

    def test_changed_message_cannot_reuse_read_item_id(self):
        self.store.set_read("fixture:H-1", True, "fixture")
        before = self.source.read_bytes()
        updated = copy.deepcopy(self.data)
        updated["inbox"][0]["summary"] = "Different important result"
        with self.assertRaises(ValueError):
            self.store.publish(updated)
        self.assertEqual(self.source.read_bytes(), before)

    def test_concurrent_content_publish_preserves_explicit_read_state(self):
        other = portal.TeamStore(self.source)
        barrier = threading.Barrier(3)
        errors = []
        proposed = copy.deepcopy(self.data)
        proposed["tasks"][0]["next_action"] = "Accepted content update"

        def act(operation):
            try:
                barrier.wait(timeout=3)
                operation()
            except Exception as exc:
                errors.append(exc)

        workers = [
            threading.Thread(
                target=act,
                args=(lambda: self.store.set_read("fixture:H-1", True, "fixture"),),
            ),
            threading.Thread(target=act, args=(lambda: other.publish(proposed),)),
        ]
        for worker in workers:
            worker.start()
        barrier.wait(timeout=3)
        for worker in workers:
            worker.join(timeout=3)
        self.assertEqual(errors, [])
        state = self.store.snapshot()
        self.assertEqual(state["inbox"][0]["read_status"], "read")
        self.assertEqual(state["tasks"][0]["next_action"], "Accepted content update")

    def test_readonly_mode_cannot_mutate_canonical_data(self):
        self.app.writable = False
        before = self.source.read_bytes()
        status, _ = self.request(
            "POST", "/api/read-state", {"id": "fixture:H-1", "read": True}, True
        )
        self.assertEqual(status, 403)
        self.assertEqual(self.source.read_bytes(), before)

    def test_unresolved_goal_cannot_be_published_as_completed(self):
        before = self.source.read_bytes()
        for indicator in (
            {"problem_status": "unresolved"},
            {"scientific_question_resolved": False},
            {"unresolved": "原问题仍未解决"},
        ):
            with self.subTest(indicator=indicator):
                proposed = copy.deepcopy(self.data)
                proposed["tasks"][0].update(status="completed", **indicator)
                with self.assertRaises(ValueError):
                    self.store.publish(proposed)
                self.assertEqual(self.source.read_bytes(), before)
        proposed["tasks"][0].update(problem_status="resolved")
        self.store.publish(proposed)
        self.assertEqual(self.store.content()["tasks"][0]["status"], "completed")

    def test_full_report_phases_and_evidence_are_projected_without_mutation(self):
        evidence = self.root / "phase.md"
        evidence.write_text("Saved phase outcome")
        proposed = copy.deepcopy(self.data)
        proposed["tasks"][0].update(
            problem_status="unresolved",
            report={
                "goal": "本来要解决的问题。",
                "work_done": "已经完成的工作。",
                "result": "实际观察到的结果。",
                "remaining": "原问题仍有缺口。",
                "next_step": "等待明确的下一步。",
                "evidence": [{"label": "报告证据", "url": str(evidence)}],
            },
            phases=[
                {
                    "id": "P1",
                    "title": "结束的试验",
                    "status": "completed",
                    "result": "有明确阶段结果。",
                    "evidence": [{"label": "阶段证据", "url": str(evidence)}],
                }
            ],
        )
        self.store.publish(proposed)
        before = self.source.read_bytes()
        task = self.store.snapshot()["tasks"][0]
        self.assertEqual(task["status"], "in_progress")
        self.assertEqual(task["report"]["remaining"], "原问题仍有缺口。")
        self.assertEqual(task["phases"][0]["status"], "completed")
        for location in (task["report"], task["phases"][0]):
            self.assertEqual(
                self.request(path=location["evidence"][0]["url"])[1],
                b"Saved phase outcome",
            )
        self.assertEqual(self.source.read_bytes(), before)

    def test_figures_require_exact_files_and_serve_only_declared_assets(self):
        with tempfile.TemporaryDirectory() as outside:
            root = Path(outside)
            html = root / "view.html"
            html.write_text(
                '<script src="assets/view.js"></script><div id="result"></div>'
            )
            javascript = root / "view.js"
            javascript.write_text(
                'document.getElementById("result").textContent="3D fixture";'
            )
            secret = root / "private.txt"
            secret.write_text("Not declared")
            proposed = copy.deepcopy(self.data)
            proposed["tasks"][0]["figures"] = [
                {
                    "label": "交互视图",
                    "url": str(html),
                    "caption": "仅展示保存的结果。",
                    "kind": "html",
                    "assets": [{"name": "assets/view.js", "url": str(javascript)}],
                }
            ]
            self.store.publish(proposed)
            self.assertFalse(
                self.store.snapshot()["tasks"][0]["figures"][0]["available"]
            )
            self.store.files.update((html.resolve(), javascript.resolve()))
            figure = self.store.snapshot()["tasks"][0]["figures"][0]
            self.assertTrue(figure["available"])
            self.assertEqual(self.request(path=figure["url"])[1], html.read_bytes())
            base = figure["url"].rsplit("/", 1)[0]
            self.assertEqual(
                self.request(path=base + "/assets/view.js")[1], javascript.read_bytes()
            )
            self.assertEqual(self.request(path=base + "/private.txt")[0], 404)
            self.assertEqual(self.request(path=base + "/%2e%2e/private.txt")[0], 404)
            connection = http.client.HTTPConnection(
                "127.0.0.1", self.server.server_port, timeout=3
            )
            connection.request("GET", figure["url"])
            response = connection.getresponse()
            policy = response.getheader("Content-Security-Policy")
            self.assertIn("sandbox allow-scripts", policy)
            self.assertNotIn("allow-same-origin", policy)
            self.assertEqual(response.getheader("Access-Control-Allow-Origin"), "null")
            response.read()
            connection.close()

    def test_atomic_replacement_sends_sse_without_polling(self):
        if not self.app.watcher.available:
            self.skipTest("Linux inotify not available")
        connection = http.client.HTTPConnection(
            "127.0.0.1", self.server.server_port, timeout=3
        )
        connection.request("GET", "/api/events")
        response = connection.getresponse()
        self.assertEqual(response.status, 200)

        def event():
            self.assertEqual(response.fp.readline().strip(), b"event: state")
            line = response.fp.readline().decode()
            self.assertEqual(response.fp.readline().strip(), b"")
            return json.loads(line.removeprefix("data: "))

        self.assertEqual(event()["tasks"][0]["title"], self.data["tasks"][0]["title"])
        updated = copy.deepcopy(self.data)
        updated["tasks"][0]["title"] = "Actual new event"
        portal.atomic_write(self.source, json.dumps(updated))
        self.assertEqual(event()["tasks"][0]["title"], "Actual new event")
        self.assertTrue(self.app.watcher.relevant(-1, 0x4000, ""))
        connection.close()

    def test_artifacts_are_declared_and_cannot_escape_roots(self):
        document = self.root / "evidence.md"
        document.write_text("Actual evidence")
        with tempfile.TemporaryDirectory() as outside:
            secret = Path(outside) / "private.txt"
            secret.write_text("Not exposed")
            (self.root / "escape").symlink_to(secret)
            data = copy.deepcopy(self.data)
            data["tasks"][0]["evidence"] = [
                {"label": "Selected", "url": str(document)},
                {"label": "Outside", "url": str(secret)},
                {"label": "Symlink", "url": str(self.root / "escape")},
                {"label": "Script", "url": "javascript:alert(1)"},
            ]
            portal.atomic_write(self.source, json.dumps(data))
            evidence = self.store.snapshot()["tasks"][0]["evidence"]
            self.assertTrue(evidence[0]["url"].startswith("/artifacts/"))
            self.assertEqual(
                self.request(path=evidence[0]["url"])[1], b"Actual evidence"
            )
            self.assertTrue(all(item["url"] is None for item in evidence[1:]))
            self.assertEqual(self.request(path="/../../private.txt")[0], 404)


if __name__ == "__main__":
    unittest.main()
