import os
import sys
import shutil
import platform
import subprocess
import click
import requests
from hubfetch import config


# terminals known to support the kitty graphics protocol
_KITTY_TERMS = {
    "TERM": {"xterm-kitty"},
    "TERM_PROGRAM": {"ghostty", "WezTerm", "Konsole"},
}


def verify_token(token: str) -> str | None:
    """
    Verify the token against the GitHub API.
    Returns the authenticated username on success, None on failure.
    """
    response = requests.get(
        "https://api.github.com/user",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
        },
    )
    if response.status_code == 200:
        return response.json().get("login")
    return None


def _detect_renderer() -> tuple[str, str]:
    """
    Detect whether the current terminal supports the kitty graphics protocol.
    Returns (renderer_name, reason_string).
    """
    term = os.environ.get("TERM", "")
    term_pgm = os.environ.get("TERM_PROGRAM", "")

    if term in _KITTY_TERMS["TERM"]:
        return "kitty", f"detected Kitty terminal (TERM={term})"

    if term_pgm in _KITTY_TERMS["TERM_PROGRAM"]:
        return "kitty", f"detected {term_pgm} (TERM_PROGRAM={term_pgm})"

    detected = term_pgm or term or "unknown terminal"
    return "chafa", f"{detected} does not support the kitty graphics protocol"

# all the stuff I do to ensure things are cross-platform 
def _get_chafa_install_cmd() -> tuple[str, list[str]] | None:
    """
    Detect the best available package manager and return
    (manager_name, install_command_args).
    Returns None if no supported package manager is found.
    """
    system = platform.system()

    if system == "Windows":
        managers = [
            ("winget", ["winget", "install", "hpjansson.Chafa"]),
            ("scoop",  ["scoop", "install", "chafa"]),
            ("choco",  ["choco", "install", "chafa", "-y"]),
        ]
    elif system == "Darwin":
        managers = [
            ("brew", ["brew", "install", "chafa"]),
        ]
    else:
        managers = [
            ("pacman", ["sudo", "pacman", "-S", "--noconfirm", "chafa"]),
            ("apt",    ["sudo", "apt", "install", "-y", "chafa"]),
            ("dnf",    ["sudo", "dnf", "install", "-y", "chafa"]),
            ("zypper", ["sudo", "zypper", "install", "-y", "chafa"]),
            ("brew",   ["brew", "install", "chafa"]),  
        ]

    for name, cmd in managers:
        # for sudo commands, check the actual binary (index 1), not sudo itself
        binary = cmd[1] if cmd[0] == "sudo" else cmd[0]
        if shutil.which(binary):
            return name, cmd

    return None


def _ensure_chafa() -> bool:
    """
    Check if chafa is available. If not, attempt to install it
    via the best available package manager.
    Returns True if chafa is available after the check.
    """
    if shutil.which("chafa"):
        return True

    result = _get_chafa_install_cmd()
    if not result:
        click.echo(
            "⚠ chafa is not installed and no supported package manager was found.\n"
            "  Please install chafa manually: https://hpjansson.org/chafa/download/",
            err=True,
        )
        return False

    manager, cmd = result

    # warn before running sudo on Linux
    if cmd[0] == "sudo":
        click.echo(f"  chafa not found — installing via {manager} (requires sudo)...")
        if not click.confirm("  This will run a sudo command. Continue?", default=True):
            click.echo(
                "  Skipping chafa install. Avatar rendering will be unavailable.\n"
                "  Install manually: https://hpjansson.org/chafa/download/"
            )
            return False
    else:
        click.echo(f"  chafa not found — installing via {manager}...")

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        click.echo(
            f"⚠ Failed to install chafa via {manager}.\n"
            "  Please install it manually: https://hpjansson.org/chafa/download/",
            err=True,
        )
        return False

    if not shutil.which("chafa"):
        click.echo(
            "⚠ chafa was installed but is not on PATH.\n"
            "  You may need to restart your terminal.",
            err=True,
        )
        return False

    click.echo("  ✓ chafa installed successfully.")
    return True


def _set_renderer(renderer: str) -> None:
    """Persist image_renderer into the config."""
    cfg = config.get_config()
    cfg["display"]["image_renderer"] = renderer
    config._write(cfg)


@click.command()
def auth():
    """Authenticate hubfetch with your GitHub account."""

    click.echo("GitHub API Authentication Setup")
    click.echo()
    click.echo("To get your GitHub Personal Access Token (PAT):")
    click.echo("1. Go to: https://github.com/settings/tokens")
    click.echo("2. Log in with your GitHub account")
    click.echo("3. Click 'Generate new token (classic)'")
    click.echo("4. Give the token a descriptive name (e.g. 'hubfetch')")
    click.echo("5. Under 'Select scopes', check 'read:user'")
    click.echo("6. Click 'Generate token' and copy it")
    click.echo()

    token = click.prompt("Enter your GitHub Personal Access Token", hide_input=True)

    if not token:
        click.echo("Error: Token cannot be empty!", err=True)
        sys.exit(1)

    if not token.startswith(("ghp_", "github_pat_")):
        click.echo(
            "Warning: Token doesn't look like a valid GitHub PAT. "
            "Classic tokens start with 'ghp_' and fine-grained with 'github_pat_'."
        )
        click.confirm("Do you want to try it anyway?", abort=True)

    click.echo()
    click.echo("Verifying token...")

    username = verify_token(token)

    if not username:
        click.echo(
            "Error: Could not authenticate with GitHub. Please check your token.",
            err=True,
        )
        sys.exit(1)

    if not config.set_credentials(token, username):
        click.echo("Failed to save credentials.", err=True)
        sys.exit(1)

    click.echo(f"Authenticated as: {username}")
    click.echo()

    # detect and persist the best renderer for this terminal session
    renderer, reason = _detect_renderer()
    _set_renderer(renderer)

    click.echo("Display Setup")
    if renderer == "kitty":
        click.echo(f"  ✓ Kitty graphics protocol enabled  ({reason})")
    else:
        click.echo(f"  ✗ Kitty graphics protocol unavailable  ({reason})")
        click.echo("  Falling back to chafa for avatar rendering...")
        click.echo()
        if _ensure_chafa():
            click.echo("  ✓ chafa is ready — your avatar will render as block art.")
        else:
            click.echo("  ✗ Avatar rendering will be unavailable until chafa is installed.")

    click.echo()
    click.echo("Run 'hubfetch' to view your GitHub stats.")