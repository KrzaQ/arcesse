from __future__ import annotations

import httpx

from arcesse.backends.base import Cookie, Solution
from arcesse.errors import BackendError, BackendUnavailableError, ChallengeFailedError


class FlareSolverrBackend:
    """FlareSolverr v3 backend."""

    def __init__(self, base_url: str = "http://localhost:8191") -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.Client(timeout=120.0)

    def _post_command(self, payload: dict) -> dict:
        try:
            resp = self._client.post(f"{self._base_url}/v1", json=payload)
        except httpx.ConnectError as exc:
            raise BackendUnavailableError(
                f"Cannot connect to FlareSolverr at {self._base_url}. "
                "Is the backend running? Try: docker compose up -d"
            ) from exc

        data = resp.json()
        if data.get("status") != "ok":
            message = data.get("message", "Unknown error from FlareSolverr")
            if "challenge" in message.lower():
                raise ChallengeFailedError(message)
            raise BackendError(message)
        return data

    def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        session: str | None = None,
        timeout: int = 60000,
    ) -> Solution:
        payload: dict = {"cmd": "request.get", "url": url, "maxTimeout": timeout}
        if session:
            payload["session"] = session
        if headers:
            payload["headers"] = headers
        return self._parse_solution(self._post_command(payload))

    def post(
        self,
        url: str,
        *,
        data: str | None = None,
        headers: dict[str, str] | None = None,
        session: str | None = None,
        timeout: int = 60000,
    ) -> Solution:
        payload: dict = {"cmd": "request.post", "url": url, "maxTimeout": timeout}
        if data:
            payload["postData"] = data
        if session:
            payload["session"] = session
        if headers:
            payload["headers"] = headers
        return self._parse_solution(self._post_command(payload))

    def create_session(self, session_id: str | None = None) -> str:
        payload: dict = {"cmd": "sessions.create"}
        if session_id:
            payload["session"] = session_id
        data = self._post_command(payload)
        return data.get("session", session_id or "")

    def destroy_session(self, session_id: str) -> None:
        self._post_command({"cmd": "sessions.destroy", "session": session_id})

    def list_sessions(self) -> list[str]:
        data = self._post_command({"cmd": "sessions.list"})
        return data.get("sessions", [])

    @staticmethod
    def _parse_solution(data: dict) -> Solution:
        sol = data["solution"]
        cookies = [
            Cookie(
                name=c["name"],
                value=c["value"],
                domain=c.get("domain", ""),
                path=c.get("path", "/"),
                expires=c.get("expiry", 0),
                secure=c.get("secure", False),
                http_only=c.get("httpOnly", False),
            )
            for c in sol.get("cookies", [])
        ]
        return Solution(
            url=sol["url"],
            status=sol["status"],
            headers=sol.get("headers", {}),
            body=sol["response"],
            cookies=cookies,
            user_agent=sol.get("userAgent", ""),
        )
