import os
from urllib.request import Request, urlopen


def main() -> None:
    host = os.getenv("ALLOWED_HOSTS", "localhost").split(",")[0].strip()
    if host == "*" or not host:
        host = "localhost"
    request = Request(
        "http://127.0.0.1:8000/_health",
        headers={"Host": host},
    )
    with urlopen(request, timeout=3) as response:
        if response.status != 200:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
