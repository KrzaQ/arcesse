# arcesse

Fetch websites behind Cloudflare protection. A lightweight Python CLI that talks to a dockerized browser backend to solve Cloudflare challenges and return clean HTML or cookies.

## Quick Start

```bash
# Start the backend
docker compose up -d

# Install the CLI
uv pip install -e .

# Fetch a page
arcesse fetch https://protected-site.com

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

arcesse uses [FlareSolverr](https://github.com/FlareSolverr/FlareSolverr) as its browser backend. The included `docker-compose.yml` runs it on port 8191:

```bash
docker compose up -d    # start
docker compose down     # stop
docker compose logs -f  # view logs
```

The backend architecture is pluggable — see `src/arcesse/backends/base.py` for the protocol that backends implement.

## Requirements

- Python 3.11+
- Docker (for the backend)
- [uv](https://docs.astral.sh/uv/) (recommended for installation)
