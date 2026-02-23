from __future__ import annotations

import html2text as _html2text

from arcesse.backends.base import Backend, Solution
from arcesse.cookies import to_json, to_netscape_jar


def fetch(
    backend: Backend,
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    data: str | None = None,
    session: str | None = None,
    timeout: int = 60000,
) -> Solution:
    """Fetch a URL through the backend."""
    if method.upper() == "POST":
        return backend.post(
            url, data=data, headers=headers, session=session, timeout=timeout
        )
    return backend.get(url, headers=headers, session=session, timeout=timeout)


def get_cookies(
    backend: Backend,
    url: str,
    *,
    session: str | None = None,
    timeout: int = 60000,
    fmt: str = "netscape",
) -> str:
    """Fetch a URL to solve the challenge, then return cookies in the requested format."""
    solution = backend.get(url, session=session, timeout=timeout)
    if fmt == "json":
        return to_json(solution.cookies)
    return to_netscape_jar(solution.cookies)


def read_html(
    backend: Backend,
    url: str,
    *,
    session: str | None = None,
    timeout: int = 60000,
) -> str:
    """Fetch a URL and convert the HTML body to readable markdown text."""
    solution = backend.get(url, session=session, timeout=timeout)
    h = _html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = True
    h.body_width = 0  # don't wrap lines
    return h.handle(solution.body)
