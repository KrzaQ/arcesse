# arcesse

Fetch websites behind Cloudflare protection. A lightweight Python CLI that talks to a dockerized browser backend to solve Cloudflare challenges and return clean HTML or cookies.

## Quick Start

```bash
# Start the backend
docker compose up -d

# Install the CLI
make install  # or: uv tool install --force -e .

# Fetch a page (raw HTML)
arcesse fetch https://protected-site.com

# Read a page (clean text/markdown)
arcesse read https://protected-site.com

# Get cookies, then reuse with curl
arcesse cookies https://protected-site.com > cookies.txt
curl -b cookies.txt https://protected-site.com/api/data
```

## Commands

### `arcesse fetch`

Fetch a URL and print the response body to stdout.

```bash
arcesse fetch https://example.com
arcesse fetch -X POST -d "key=value" https://example.com/api
arcesse fetch -H "Accept: application/json" https://example.com
arcesse fetch -o page.html https://example.com

# File downloads are auto-detected — saves with the suggested filename
arcesse fetch https://example.com/files/report.pdf
arcesse fetch -o report.pdf https://example.com/files/report.pdf
```

| Flag | Short | Description |
|------|-------|-------------|
| `--method` | `-X` | HTTP method (GET or POST) |
| `--header` | `-H` | Request header (`Name: Value`), repeatable |
| `--data` | `-d` | POST body |
| `--output` | `-o` | Write to file instead of stdout |
| `--timeout` | `-t` | Timeout in milliseconds |
| `--backend-url` | `-b` | Backend service URL |
| `--session` | `-s` | Session ID (persistent browser instance) |

### `arcesse read`

Fetch a URL and convert to readable markdown text (via html2text).

```bash
arcesse read https://example.com
arcesse read -o page.md https://example.com
```

| Flag | Short | Description |
|------|-------|-------------|
| `--output` | `-o` | Write to file instead of stdout |
| `--timeout` | `-t` | Timeout in milliseconds |
| `--backend-url` | `-b` | Backend service URL |
| `--session` | `-s` | Session ID |

### `arcesse cookies`

Solve a Cloudflare challenge and print cookies.

```bash
# Netscape cookie jar format (default, compatible with curl -b)
arcesse cookies https://protected-site.com > cookies.txt

# JSON format
arcesse cookies -f json https://protected-site.com
```

| Flag | Short | Description |
|------|-------|-------------|
| `--format` | `-f` | Output format: `netscape` (default) or `json` |
| `--timeout` | `-t` | Timeout in milliseconds |
| `--backend-url` | `-b` | Backend service URL |
| `--session` | `-s` | Session ID |

## Configuration

| Setting | Env var | Default |
|---------|---------|---------|
| Backend URL | `ARCESSE_BACKEND_URL` | `http://localhost:8191` |
| Timeout | `ARCESSE_TIMEOUT` | `60000` (ms) |

CLI flags override env vars, which override defaults.

## Backend

The default backend is a custom [Camoufox](https://camoufox.com/)-based service (`service/`) with WebGL spoofing, browser fingerprint randomization, and origin warm-up to bypass bot detection. It speaks the FlareSolverr v3 API.

[FlareSolverr](https://github.com/FlareSolverr/FlareSolverr) and [Byparr](https://github.com/ThePhaseless/Byparr) are available as optional profiles:

```bash
docker compose up -d                          # Camoufox (default, port 8191)
docker compose --profile flaresolverr up -d   # FlareSolverr (port 8192)
docker compose --profile byparr up -d         # Byparr (port 8193)

# Use an alternative backend
arcesse --backend-url http://localhost:8192 fetch https://example.com
```

Ports are configurable via `.env` or environment variables: `CAMOUFOX_PORT`, `FLARESOLVERR_PORT`, `BYPARR_PORT`.

The backend architecture is pluggable — see `src/arcesse/backends/base.py` for the protocol that backends implement.

## Requirements

- Python 3.11+
- Docker (for the backend)
- [uv](https://docs.astral.sh/uv/) (recommended for installation)
