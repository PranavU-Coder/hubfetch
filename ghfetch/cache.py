import json
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path


CACHE_DIR = Path.home() / ".cache" / "ghfetch"
META_FILE = CACHE_DIR / "meta.json"
REFRESH_AFTER = timedelta(hours=6)


def _load_meta() -> dict:
    """Read cached metadata, returning empty dict if it doesn't exist yet."""
    if META_FILE.exists():
        with open(META_FILE, "r") as f:
            return json.load(f)
    return {}


def _save_meta(meta: dict) -> None:
    """Persist metadata to disk."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(META_FILE, "w") as f:
        json.dump(meta, f, indent=2)


def _download(avatar_url: str, dest: Path) -> bool:
    """Fetch avatar bytes from URL and write to dest."""
    try:
        response = requests.get(avatar_url, timeout=30)
        response.raise_for_status()
        dest.write_bytes(response.content)
        return True
    except Exception:
        return False


def avatar_path(username: str) -> Path:
    """Return the local path where the avatar is (or will be) cached."""
    return CACHE_DIR / f"{username}.png"


def ensure_avatar(username: str, current_avatar_url: str) -> Path | None:
    """
    Return a valid local path to the user's avatar, downloading or refreshing
    it as needed.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    dest = avatar_path(username)
    meta = _load_meta()
    now = datetime.now(timezone.utc)

    last_checked_raw = meta.get("last_checked")
    cached_url = meta.get("avatar_url")

    # first run
    if not dest.exists() or not last_checked_raw:
        if _download(current_avatar_url, dest):
            _save_meta(
                {"avatar_url": current_avatar_url, "last_checked": now.isoformat()}
            )
            return dest
        return None

    last_checked = datetime.fromisoformat(last_checked_raw)

    # Within 6 hours — serve from cache
    if now - last_checked < REFRESH_AFTER:
        return dest

    # Past 6 hours — check if avatar URL changed
    if current_avatar_url != cached_url:
        # URL changed → user updated their avatar, re-download
        _download(current_avatar_url, dest)

    # Either way, update the timestamp and stored URL
    _save_meta({"avatar_url": current_avatar_url, "last_checked": now.isoformat()})
    return dest
