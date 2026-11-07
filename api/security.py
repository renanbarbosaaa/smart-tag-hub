import secrets
import time
from collections import defaultdict, deque
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError

from api.config import Settings

_password_hash = PasswordHash.recommended()


class AdminPageLoginRequired(Exception):
    pass


class LoginAttemptLimiter:
    def __init__(self, max_attempts: int = 5, window_seconds: int = 300) -> None:
        self._max_attempts = max_attempts
        self._window_seconds = window_seconds
        self._attempts: dict[str, deque[float]] = defaultdict(deque)

    def is_allowed(self, key: str) -> bool:
        self._prune(key)
        return len(self._attempts[key]) < self._max_attempts

    def record_failure(self, key: str) -> None:
        self._prune(key)
        self._attempts[key].append(time.monotonic())

    def reset(self, key: str | None = None) -> None:
        if key is None:
            self._attempts.clear()
        else:
            self._attempts.pop(key, None)

    def _prune(self, key: str) -> None:
        cutoff = time.monotonic() - self._window_seconds
        attempts = self._attempts[key]
        while attempts and attempts[0] < cutoff:
            attempts.popleft()


login_attempt_limiter = LoginAttemptLimiter()


def _secure_compare(value: str, expected: str) -> bool:
    return secrets.compare_digest(value.encode("utf-8"), expected.encode("utf-8"))


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_admin_credentials(username: str, password: str, settings: Settings) -> bool:
    try:
        password_valid = (
            _password_hash.verify(password, settings.admin_password_hash)
            if settings.admin_password_hash
            else False
        )
    except UnknownHashError:
        password_valid = False
    username_valid = _secure_compare(username, settings.admin_username)
    return username_valid and password_valid


def require_admin_api(request: Request) -> None:
    if request.session.get("is_admin") is not True:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação administrativa necessária.",
        )


def require_admin_page(request: Request) -> None:
    if request.session.get("is_admin") is not True:
        raise AdminPageLoginRequired


def get_csrf_token(request: Request) -> str:
    token = request.session.get("csrf_token")
    if not isinstance(token, str):
        token = secrets.token_urlsafe(32)
        request.session["csrf_token"] = token
    return token


def validate_csrf(request: Request, token: str) -> None:
    expected = request.session.get("csrf_token")
    if not isinstance(expected, str) or not _secure_compare(token, expected):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sessão do formulário expirada. Tente novamente.",
        )


AdminApiDep = Annotated[None, Depends(require_admin_api)]
AdminPageDep = Annotated[None, Depends(require_admin_page)]
