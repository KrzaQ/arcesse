# arcesse

CLI tool + dockerized backend for fetching websites behind Cloudflare protection.

## Architecture

Split into a lightweight Python CLI and a dockerized browser backend (currently FlareSolverr).

```
src/arcesse/
  cli.py              # Click CLI entry point (arcesse fetch, arcesse cookies)
  client.py            # Orchestration layer between CLI and backends
  config.py            # Config resolution: CLI flag > env var > default
  cookies.py           # Cookie formatting (Netscape jar for curl, JSON)
  errors.py            # Exception hierarchy (ArcesseError base)
  backends/
    base.py            # Backend Protocol + Solution/Cookie dataclasses
    flaresolverr.py    # FlareSolverr v3 implementation
```

## Key Design Decisions

- **Backend Protocol** (`backends/base.py`): Uses `typing.Protocol` (structural subtyping). New backends just need matching method signatures — no inheritance required.
- **Sync only**: httpx in sync mode. One request per invocation, no need for async.
- **stdout/stderr split**: Content goes to stdout, status/errors to stderr. Safe for piping.
- **Config precedence**: CLI flag > `ARCESSE_BACKEND_URL` / `ARCESSE_TIMEOUT` env vars > defaults (`http://localhost:8191`, 60000ms).

## Development

```bash
docker compose up -d          # Start FlareSolverr backend
uv sync                       # Install deps
uv run arcesse --help         # Run CLI
```

## Adding a New Backend

1. Create `src/arcesse/backends/newbackend.py` with a class matching the `Backend` protocol methods: `get()`, `post()`, `create_session()`, `destroy_session()`, `list_sessions()`
2. Update `_make_backend()` in `cli.py` to support selecting it

## Testing

```bash
uv run arcesse fetch https://example.com
uv run arcesse cookies https://nowsecure.nl
uv run arcesse cookies -f json https://example.com
```
