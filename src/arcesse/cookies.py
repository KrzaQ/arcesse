from __future__ import annotations

import json

from arcesse.backends.base import Cookie


def to_netscape_jar(cookies: list[Cookie]) -> str:
    """Format cookies as a Netscape cookie jar file (compatible with curl -b)."""
    lines = [
        "# Netscape HTTP Cookie File",
        "# https://curl.se/docs/http-cookies.html",
        "",
    ]
    for c in cookies:
        prefix = "#HttpOnly_" if c.http_only else ""
        tailmatch = "TRUE" if c.domain.startswith(".") else "FALSE"
        secure = "TRUE" if c.secure else "FALSE"
        expires = str(int(c.expires)) if c.expires else "0"
        lines.append(
            f"{prefix}{c.domain}\t{tailmatch}\t{c.path}\t{secure}\t{expires}\t{c.name}\t{c.value}"
        )
    return "\n".join(lines) + "\n"


def to_json(cookies: list[Cookie]) -> str:
    """Format cookies as a JSON array."""
    return json.dumps(
        [
            {
                "name": c.name,
                "value": c.value,
                "domain": c.domain,
                "path": c.path,
                "expires": c.expires,
                "secure": c.secure,
                "httpOnly": c.http_only,
            }
            for c in cookies
        ],
        indent=2,
    )
