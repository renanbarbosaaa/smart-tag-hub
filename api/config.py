import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path, PurePosixPath

from dotenv import load_dotenv
from sqlalchemy.engine import make_url

_DEFAULT_SECRET = "development-only-secret-change-me"
_INSECURE_SECRETS = {
    _DEFAULT_SECRET,
    "substitua-por-uma-chave-aleatoria-longa",
    "uma-chave-aleatoria-com-pelo-menos-32-caracteres",
}


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class Settings:
    environment: str
    database_url: str
    secret_key: str
    admin_username: str
    admin_password_hash: str
    allowed_hosts: tuple[str, ...]
    session_secure_cookie: bool
    database_url_explicit: bool = False
    session_max_age: int = 28_800

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    def validate(self) -> None:
        if not self.is_production:
            return
        if self.secret_key in _INSECURE_SECRETS or len(self.secret_key) < 32:
            raise RuntimeError(
                "SECRET_KEY deve ser aleatória e ter ao menos 32 caracteres."
            )
        if not self.admin_password_hash.startswith("$argon2"):
            raise RuntimeError(
                "ADMIN_PASSWORD_HASH deve conter um hash Argon2 válido em produção."
            )
        if "*" in self.allowed_hosts:
            raise RuntimeError(
                "ALLOWED_HOSTS deve listar os domínios usados em produção."
            )
        if not self.session_secure_cookie:
            raise RuntimeError("SESSION_SECURE_COOKIE deve ser true em produção.")
        if not self.database_url_explicit:
            raise RuntimeError(
                "DATABASE_URL deve ser definida explicitamente em produção."
            )
        self._validate_database_persistence()

    def _validate_database_persistence(self) -> None:
        url = make_url(self.database_url)
        if url.get_backend_name() != "sqlite":
            return
        database = url.database
        is_absolute = Path(database).is_absolute() if database else False
        is_posix_absolute = PurePosixPath(database).is_absolute() if database else False
        if (
            not database
            or database == ":memory:"
            or not (is_absolute or is_posix_absolute)
        ):
            raise RuntimeError(
                "SQLite em produção exige um caminho absoluto em volume persistente."
            )


@lru_cache
def get_settings() -> Settings:
    load_dotenv()
    environment = os.getenv("ENVIRONMENT", "development").strip().lower()
    hosts = tuple(
        host.strip()
        for host in os.getenv("ALLOWED_HOSTS", "*").split(",")
        if host.strip()
    )
    database_url = os.getenv("DATABASE_URL", "").strip()
    return Settings(
        environment=environment,
        database_url=database_url or "sqlite+aiosqlite:///./smart_tag_hub.db",
        database_url_explicit=bool(database_url),
        secret_key=os.getenv("SECRET_KEY") or _DEFAULT_SECRET,
        admin_username=os.getenv("ADMIN_USERNAME", "admin"),
        admin_password_hash=os.getenv("ADMIN_PASSWORD_HASH", ""),
        allowed_hosts=hosts or ("*",),
        session_secure_cookie=_as_bool(
            os.getenv(
                "SESSION_SECURE_COOKIE",
                "true" if environment == "production" else "false",
            )
        ),
    )
