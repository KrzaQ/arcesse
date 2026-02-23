from __future__ import annotations

import click

from arcesse.backends.flaresolverr import FlareSolverrBackend
from arcesse.client import fetch, get_cookies, read_html
from arcesse.config import resolve_backend_url, resolve_timeout
from arcesse.errors import ArcesseError


def _log(msg: str) -> None:
    click.echo(msg, err=True)


def _make_backend(backend_url: str) -> FlareSolverrBackend:
    return FlareSolverrBackend(base_url=backend_url)


def _parse_headers(header_values: tuple[str, ...]) -> dict[str, str] | None:
    if not header_values:
        return None
    headers: dict[str, str] = {}
    for h in header_values:
        if ":" not in h:
            _log(f"arcesse: ignoring malformed header: {h}")
            continue
        key, _, value = h.partition(":")
        headers[key.strip()] = value.strip()
    return headers or None


@click.group()
@click.version_option()
def main() -> None:
    """arcesse - fetch websites behind Cloudflare protection."""


@main.command("fetch")
@click.argument("url")
@click.option("--method", "-X", default="GET", help="HTTP method (GET or POST).")
@click.option(
    "--header", "-H", multiple=True, help="Request header (Name: Value). Repeatable."
)
@click.option("--data", "-d", default=None, help="POST data.")
@click.option(
    "--output",
    "-o",
    default=None,
    type=click.Path(),
    help="Write response to file instead of stdout.",
)
@click.option("--timeout", "-t", default=None, type=int, help="Timeout in ms.")
@click.option("--backend-url", "-b", default=None, help="Backend service URL.")
@click.option("--session", "-s", default=None, help="Session ID for the backend.")
def fetch_cmd(
    url: str,
    method: str,
    header: tuple[str, ...],
    data: str | None,
    output: str | None,
    timeout: int | None,
    backend_url: str | None,
    session: str | None,
) -> None:
    """Fetch a URL and print the response body."""
    resolved_url = resolve_backend_url(backend_url)
    resolved_timeout = resolve_timeout(timeout)
    headers = _parse_headers(header)
    backend = _make_backend(resolved_url)

    _log(f"arcesse: fetching {url} via {resolved_url}")

    try:
        solution = fetch(
            backend,
            url,
            method=method,
            headers=headers,
            data=data,
            session=session,
            timeout=resolved_timeout,
        )
    except ArcesseError as exc:
        _log(f"arcesse: error: {exc}")
        raise SystemExit(1)

    _log(f"arcesse: status {solution.status}, {len(solution.body)} bytes")

    if output:
        with open(output, "w") as f:
            f.write(solution.body)
        _log(f"arcesse: wrote to {output}")
    else:
        click.echo(solution.body)


@main.command("cookies")
@click.argument("url")
@click.option(
    "--format",
    "-f",
    "fmt",
    type=click.Choice(["netscape", "json"]),
    default="netscape",
    help="Cookie output format.",
)
@click.option("--timeout", "-t", default=None, type=int, help="Timeout in ms.")
@click.option("--backend-url", "-b", default=None, help="Backend service URL.")
@click.option("--session", "-s", default=None, help="Session ID for the backend.")
def cookies_cmd(
    url: str,
    fmt: str,
    timeout: int | None,
    backend_url: str | None,
    session: str | None,
) -> None:
    """Solve Cloudflare challenge and print cookies."""
    resolved_url = resolve_backend_url(backend_url)
    resolved_timeout = resolve_timeout(timeout)
    backend = _make_backend(resolved_url)

    _log(f"arcesse: solving challenge for {url} via {resolved_url}")

    try:
        cookie_text = get_cookies(
            backend,
            url,
            session=session,
            timeout=resolved_timeout,
            fmt=fmt,
        )
    except ArcesseError as exc:
        _log(f"arcesse: error: {exc}")
        raise SystemExit(1)

    click.echo(cookie_text)


@main.command("read")
@click.argument("url")
@click.option(
    "--output",
    "-o",
    default=None,
    type=click.Path(),
    help="Write response to file instead of stdout.",
)
@click.option("--timeout", "-t", default=None, type=int, help="Timeout in ms.")
@click.option("--backend-url", "-b", default=None, help="Backend service URL.")
@click.option("--session", "-s", default=None, help="Session ID for the backend.")
def read_cmd(
    url: str,
    output: str | None,
    timeout: int | None,
    backend_url: str | None,
    session: str | None,
) -> None:
    """Fetch a URL and print as readable text."""
    resolved_url = resolve_backend_url(backend_url)
    resolved_timeout = resolve_timeout(timeout)
    backend = _make_backend(resolved_url)

    _log(f"arcesse: reading {url} via {resolved_url}")

    try:
        text = read_html(
            backend,
            url,
            session=session,
            timeout=resolved_timeout,
        )
    except ArcesseError as exc:
        _log(f"arcesse: error: {exc}")
        raise SystemExit(1)

    if output:
        with open(output, "w") as f:
            f.write(text)
        _log(f"arcesse: wrote to {output}")
    else:
        click.echo(text)
