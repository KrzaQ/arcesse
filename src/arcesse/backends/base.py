from __future__ import annotations

import dataclasses
from typing import Protocol


@dataclasses.dataclass(frozen=True, slots=True)
class Cookie:
    """A single cookie from the backend response."""

    name: str
    value: str
    domain: str
    path: str
    expires: float  # unix timestamp; 0 = session
    secure: bool
    http_only: bool


@dataclasses.dataclass(frozen=True, slots=True)
class Solution:
    """The result of a backend request."""

    url: str
    status: int
    headers: dict[str, str]
    body: str
    cookies: list[Cookie]
    user_agent: str


class Backend(Protocol):
    """Protocol that all backends must satisfy."""

    def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        session: str | None = None,
        timeout: int = 60000,
    ) -> Solution: ...

    def post(
        self,
        url: str,
        *,
        data: str | None = None,
        headers: dict[str, str] | None = None,
        session: str | None = None,
        timeout: int = 60000,
    ) -> Solution: ...

    def create_session(self, session_id: str | None = None) -> str: ...

    def destroy_session(self, session_id: str) -> None: ...

    def list_sessions(self) -> list[str]: ...
