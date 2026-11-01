# Private team portal

Use `scripts/team_portal.py` with the bundled `assets/team-portal.html` when the human requests a Task List and Mailbox webpage. It uses Python 3.11+ and the standard library on Linux. Keep the service temporary and bound to a Tailnet address; retain the coordination data when the service stops.

## Canonical data and ownership

The lead owns one UTF-8 `team-state.json`. Required fields:

```json
{
  "schema_version": 1,
  "team_id": "example",
  "title": "团队工作台",
  "updated_at": "2026-11-02T00:00:00Z",
  "evidence_checked_at": "2026-11-01T00:00:00Z",
  "members": [],
  "tasks": [],
  "inbox": []
}
```

Tasks use `id`, `title`, `question`, `owner`, `status`, `execution_state`, `blocker`, `next_action`, `acceptance`, and `evidence`. Add `completed_delivery` and `unresolved` to distinguish a finished diagnostic from an answered scientific question. Inbox entries use `id`, `created_at`, `from`, `title`, `summary`, `significance`, `decision_needed`, `evidence`, `delivery_status`, and `read_status`. Evidence entries contain `label` and `url`.

Before enabling live write operations, the data owner must accept this contract:

- All updates use the helper's serialized gateway: acquire `.team-state.lock` beside the JSON, reread current data, validate it, then replace it atomically. The gateway is the sole write path; do not overwrite it with an independently edited snapshot.
- The webpage may change only the known inbox item's `read_status`, `read_updated_at`, and `read_evidence`, plus global `updated_at`. It cannot change delivery, decisions, tasks, evidence, budget, or authorization. Repeating the same requested status is idempotent.
- A web action records `source=explicit_web_action`, the peer address, and `human_identity_verified=false`. It is a shared visitor mark, without individual user authentication. Viewing a message does not write anything.
- The lead publishes content through `--publish`. Existing read fields are preserved. New important content needs a new immutable inbox ID. Human text instructions use `--mark-id` and `--read-status` through the same gateway.
- If the project already has a Markdown renderer, provide its trusted command with `--render-command`. It runs under the same lock after canonical writes. The helper does not keep a second read-state database or write a competing set of project views.

Example lead operations; keep the renderer command last:

```bash
python /path/to/team_portal.py --state /coord/team-state.json \
  --publish /coord/proposed-state.json \
  --render-command python /coord/render_views.py

python /path/to/team_portal.py --state /coord/team-state.json \
  --mark-id example:H-001 --read-status read \
  --event-source explicit_human_instruction --actor lead \
  --render-command python /coord/render_views.py
```

## Run privately

Check the current Tailnet address, MagicDNS name, and free port once. Start a foreground process or a transient runtime unit, without installing or enabling a boot service:

```bash
systemd-run --user --collect --unit=team-portal \
  --property=Type=notify --property=MemoryMax=256M --property=Restart=no \
  python /path/to/team_portal.py \
  --state /coord/team-state.json \
  --bind <tailnet-ip> --port <port> --public-host <magicdns-name> \
  --artifact-root /explicit/evidence/root \
  --allow-read-writes \
  --render-command python /coord/render_views.py
```

Omit `--allow-read-writes` until the data owner has accepted the write handoff. Tailnet ACLs govern access; this helper adds no separate user login. Only declared evidence files under the selected roots are served, with no directory listing. HTTP/HTTPS and T3 thread links remain external links; unsupported schemes are not clickable.

The server watches input-file events through Linux inotify and sends SSE snapshots. The browser closes failed streams and offers manual refresh/reconnect. Without file events, use explicit refresh. Neither path polls. These updates do not wake an agent or authorize new work.

Verify the concrete MagicDNS URL returns the intended page and canonical state, that the listener binds only the intended address, and that read/unread works using a disposable fixture. Never mark real human messages as read for testing. Test restart recovery and rejected mutations. Inspect the page's readability at desktop and mobile widths.

Give the human the actual private URL and a stop command:

```bash
systemctl --user stop team-portal
```

Stopping or rebooting removes the runtime service; canonical data remains. Keep private URLs and actual team data out of public commits.
