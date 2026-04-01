import os
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "ghfetch"
CONFIG_FILE = CONFIG_DIR / "config.json"

ENV_TOKEN = "GHFETCH_TOKEN"
ENV_USERNAME = "GHFETCH_USERNAME"

_DEFAULTS: dict = {
    "token": "",
    "username": "",
    "display": {
        "image_renderer": "auto",
        "image_size": 40,
        "show": {
            "bio": True,
            "repositories": True,
            "forks": True,
            "stars": True,
            "starred": True,
            "followers": True,
            "following": True,
            "commits": True,
            "issues": True,
            "prs": True,
            "top_language": True,
            "best_day": True,
        },
        "colors": {
            "user": "bold cyan",
            "bio": "italic dim",
            "repositories": "bold green",
            "forks": "green",
            "stars": "bold yellow",
            "starred": "bold magenta",
            "followers": "bold blue",
            "following": "bold red",
            "commits": "cyan",
            "issues": "yellow",
            "prs": "magenta",
            "top_language": "blue",
            "best_day": "red",
        },
    },
}


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base so missing keys fall back to defaults."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _write(data: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _read() -> dict:
    """
    Read config file, returning defaults if the file is missing or corrupt.
    Separating this out means every caller gets the same safe read behaviour.
    """
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except OSError, json.JSONDecodeError:
        _write(_DEFAULTS.copy())
        return _DEFAULTS.copy()


def init_config() -> None:
    """Create config dir and file with defaults if they don't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        _write(_DEFAULTS.copy())


def get_config() -> dict:
    """
    Load config, deep-merging with defaults so any missing keys
    still get display defaults. Env vars override token and username.
    """
    init_config()
    data = _read()
    merged = _deep_merge(_DEFAULTS, data)

    if token := os.environ.get(ENV_TOKEN):
        merged["token"] = token
    if username := os.environ.get(ENV_USERNAME):
        merged["username"] = username

    return merged


def get_credentials() -> dict:
    """Convenience wrapper, returns just token and username."""
    cfg = get_config()
    return {"token": cfg["token"], "username": cfg["username"]}


def set_credentials(token: str, username: str) -> bool:
    """
    Persist token and username without touching display settings.
    Uses _read() so a corrupt/missing file never causes a crash here.
    """
    try:
        init_config()
        data = _read()
        data["token"] = token
        data["username"] = username
        _write(data)
        return True
    except OSError:
        return False


def has_credentials() -> bool:
    creds = get_credentials()
    return bool(creds.get("token")) and bool(creds.get("username"))


def generate_default_config() -> None:
    """Write a fresh default config, preserving existing token/username."""
    init_config()
    existing = _read()
    fresh = _DEFAULTS.copy()
    fresh["token"] = existing.get("token", "")
    fresh["username"] = existing.get("username", "")
    _write(fresh)
