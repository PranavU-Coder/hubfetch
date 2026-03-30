import os
import json
from pathlib import Path

# config file lives at ~/.config/ghfetch/config.json

CONFIG_DIR = Path.home() / ".config" / "ghfetch"
CONFIG_FILE = CONFIG_DIR / "config.json"
ENV_TOKEN = "GHFETCH_TOKEN"
ENV_USERNAME = "GHFETCH_USERNAME"

_DEFAULTS = {
    "token": "",
    "username": "",
}


def init_config() -> None:
    """
    Create the config directory and file if they don't exist.
    """
    CONFIG_DIR.mkdir(
        parents=True, exist_ok=True
    )  # 0o755 is the default on most systems

    if not CONFIG_FILE.exists():
        _write(_DEFAULTS.copy())


def get_credentials() -> dict:
    """
    Return credentials, with environment variables taking priority over the config file.
    """
    init_config()

    with open(CONFIG_FILE, "r") as f:
        data = json.load(f)

    # env vars override whatever is in the config file
    if token := os.environ.get(ENV_TOKEN):
        data["token"] = token

    if username := os.environ.get(ENV_USERNAME):
        data["username"] = username

    return data


def set_credentials(token: str, username: str) -> bool:
    """
    Persist token and username to the config file.
    """

    try:
        init_config()
        _write({"token": token, "username": username})
        return True
    except OSError:
        return False


def has_credentials() -> bool:
    """
    Check whether valid credentials are present.
    """
    creds = get_credentials()
    return bool(creds.get("token")) and bool(creds.get("username"))


def _write(data: dict) -> None:
    """Write data to the config file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)
