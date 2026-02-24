# arcesse

CLI tool + dockerized backend for fetching websites behind Cloudflare protection.

## Architecture

Split into a lightweight Python CLI and a dockerized browser backend.

Default backend is a custom Camoufox-based service (`service/`) that speaks the FlareSolverr v3 API. FlareSolverr itself is available as an optional profile.

```
src/arcesse/
  cli.py              # Click CLI entry point (arcesse fetch, arcesse read, arcesse cookies)
  client.py            # Orchestration layer between CLI and backends (fetch, read_html, get_cookies)
  config.py            # Config resolution: CLI flag > env var > default
  cookies.py           # Cookie formatting (Netscape jar for curl, JSON)
  errors.py            # Exception hierarchy (ArcesseError base)
  backends/
    base.py            # Backend Protocol + Solution/Cookie dataclasses
    flaresolverr.py    # FlareSolverr v3 implementation (also used by Camoufox service)

service/
  app.py              # FastAPI service: Camoufox browser with FlareSolverr-compatible API
  Dockerfile          # Python + Camoufox + browser deps
  pyproject.toml      # Service dependencies
```

## Key Design Decisions

- **Backend Protocol** (`backends/base.py`): Uses `typing.Protocol` (structural subtyping). New backends just need matching method signatures — no inheritance required.
- **Sync only**: httpx in sync mode. One request per invocation, no need for async.
- **stdout/stderr split**: Content goes to stdout, status/errors to stderr. Safe for piping.
- **Config precedence**: CLI flag > `ARCESSE_BACKEND_URL` / `ARCESSE_TIMEOUT` env vars > defaults (`http://localhost:8191`, 60000ms).
- **Camoufox service** (`service/app.py`): FlareSolverr-compatible API over Camoufox. Key anti-detection: WebGL spoofing via real device fingerprints (`block_webgl=False`), origin warm-up navigation (produces `Referer` + `Sec-Fetch-Site: same-origin`), `humanize=True`, `geoip=True`, `ff_version=147`.
- **Download detection**: The Camoufox service auto-detects browser file downloads via Playwright's `page.on("download")` event. Downloads are base64-encoded in `solution.response` with `isDownload: true` and `filename` fields. The CLI decodes and writes to file automatically (uses suggested filename if `-o` not given). Backward-compatible — other backends simply never set these fields.

## Development

```bash
docker compose up -d          # Start Camoufox backend (default)
uv sync                       # Install deps
uv run arcesse --help         # Run CLI

# Alternative backends (optional profiles):
docker compose --profile flaresolverr up -d   # port 8192
docker compose --profile byparr up -d         # port 8193
arcesse --backend-url http://localhost:8192 fetch https://example.com
```

## Adding a New Backend

1. Create `src/arcesse/backends/newbackend.py` with a class matching the `Backend` protocol methods: `get()`, `post()`, `create_session()`, `destroy_session()`, `list_sessions()`
2. Update `_make_backend()` in `cli.py` to support selecting it

## Testing

```bash
uv run arcesse fetch https://example.com
uv run arcesse read https://example.com
uv run arcesse cookies https://nowsecure.nl
uv run arcesse cookies -f json https://example.com

# File downloads (auto-detected, saves with suggested filename)
uv run arcesse fetch https://gamefaqs.gamespot.com/gba/561356-golden-sun-the-lost-age/saves/28077
uv run arcesse fetch -o save.txt https://gamefaqs.gamespot.com/gba/561356-golden-sun-the-lost-age/saves/28077
```
