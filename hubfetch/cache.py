import json
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path


CACHE_DIR = Path.home() / ".cache" / "hubfetch"
META_FILE  = CACHE_DIR / "meta.json"
STATS_FILE = CACHE_DIR / "stats.json"

AVATAR_REFRESH = timedelta(hours=6)
STATS_REFRESH  = timedelta(hours=1)


def _load_json(path: Path) -> dict:
    """Read a JSON file, returning an empty dict if it doesn't exist or is corrupt."""
    if path.exists():
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_json(path: Path, data: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _is_stale(timestamp_iso: str | None, max_age: timedelta) -> bool:
    """Return True if the timestamp is missing or older than max_age."""
    if not timestamp_iso:
        return True
    last = datetime.fromisoformat(timestamp_iso)
    return datetime.now(timezone.utc) - last > max_age


def avatar_path(username: str) -> Path:
    """Return the local path where the avatar is (or will be) cached."""
    return CACHE_DIR / f"{username}.png"


def ensure_avatar(username: str, current_avatar_url: str) -> Path | None:
    """
    Return a valid local path to the user's avatar, downloading or
    refreshing it as needed every 6 hours.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    dest             = avatar_path(username)
    meta             = _load_json(META_FILE)
    now              = datetime.now(timezone.utc).isoformat()
    cached_url       = meta.get("avatar_url")
    last_checked_raw = meta.get("avatar_last_checked")

    # first run
    if not dest.exists() or not last_checked_raw:
        if _download_avatar(current_avatar_url, dest):
            meta.update({"avatar_url": current_avatar_url, "avatar_last_checked": now})
            _save_json(META_FILE, meta)
            return dest
        return None

    # within 6 hours, serve from disk
    if not _is_stale(last_checked_raw, AVATAR_REFRESH):
        return dest

    # past 6 hours, re-download only if URL changed
    if current_avatar_url != cached_url:
        _download_avatar(current_avatar_url, dest)

    meta.update({"avatar_url": current_avatar_url, "avatar_last_checked": now})
    _save_json(META_FILE, meta)

    if not dest.exists():
        return None

    return dest


def _download_avatar(url: str, dest: Path) -> bool:
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        dest.write_bytes(response.content)
        return True
    except Exception:
        return False


def get_cached_stats() -> dict | None:
    """
    Return cached stats if they're less than 1 hour old, otherwise None.
    """
    data = _load_json(STATS_FILE)
    if not data:
        return None
    if _is_stale(data.get("_cached_at"), STATS_REFRESH):
        return None
    return {k: v for k, v in data.items() if not k.startswith("_")}


def save_stats(stats: dict) -> None:
    """Persist stats to disk with a timestamp."""
    payload = {**stats, "_cached_at": datetime.now(timezone.utc).isoformat()}
    _save_json(STATS_FILE, payload)