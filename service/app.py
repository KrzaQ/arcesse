"""FlareSolverr-compatible API service backed by Camoufox."""

from __future__ import annotations

import logging
import os
import time
from urllib.parse import urlparse

from camoufox.sync_api import Camoufox
from fastapi import FastAPI
from pydantic import BaseModel

log = logging.getLogger("arcesse-service")
logging.basicConfig(
    level=getattr(logging, os.environ.get("LOG_LEVEL", "info").upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
)

app = FastAPI()


class RequestBody(BaseModel):
    cmd: str
    url: str = ""
    maxTimeout: int = 60000


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/v1")
def handle_v1(body: RequestBody) -> dict:
    if body.cmd != "request.get":
        return {"status": "error", "message": f"Unsupported command: {body.cmd}"}

    if not body.url:
        return {"status": "error", "message": "Missing url"}

    timeout_s = body.maxTimeout / 1000
    log.info("Fetching %s (timeout=%ss)", body.url, timeout_s)
    start = time.monotonic()

    try:
        with Camoufox(
            headless="virtual",
            humanize=True,
            geoip=True,
            locale="en-US",
            block_webgl=False,
            ff_version=147,
            i_know_what_im_doing=True,
        ) as browser:
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.new_page()

            # Navigate to the site origin first so the real request has
            # Referer and Sec-Fetch-Site: same-origin (like a real user).
            parsed = urlparse(body.url)
            origin = f"{parsed.scheme}://{parsed.netloc}/"
            page.goto(origin, timeout=timeout_s * 1000, wait_until="domcontentloaded")

            page.goto(body.url, timeout=timeout_s * 1000, wait_until="domcontentloaded")

            # Wait for page to settle (Cloudflare challenges, lazy JS, etc.)
            elapsed = time.monotonic() - start
            remaining_ms = max((timeout_s - elapsed) * 1000, 1000)
            try:
                page.wait_for_load_state("networkidle", timeout=remaining_ms)
            except Exception:
                pass

            html = page.content()
            cookies_raw = context.cookies()
            user_agent = page.evaluate("() => navigator.userAgent")
            final_url = page.url
            page.close()

        cookies = [
            {
                "name": c["name"],
                "value": c["value"],
                "domain": c.get("domain", ""),
                "path": c.get("path", "/"),
                "expiry": c.get("expires", 0),
                "secure": c.get("secure", False),
                "httpOnly": c.get("httpOnly", False),
            }
            for c in cookies_raw
        ]

        elapsed = time.monotonic() - start
        log.info("Fetched %s in %.1fs", body.url, elapsed)

        return {
            "status": "ok",
            "message": "",
            "solution": {
                "url": final_url,
                "status": 200,
                "response": html,
                "cookies": cookies,
                "userAgent": user_agent,
                "headers": {},
            },
            "startTimestamp": int(start * 1000),
            "endTimestamp": int(time.monotonic() * 1000),
        }
    except Exception as exc:
        log.exception("Failed to fetch %s", body.url)
        return {"status": "error", "message": str(exc)}
