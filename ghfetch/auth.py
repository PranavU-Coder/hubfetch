import os
import sys
import shutil
import subprocess

import click
import requests

from ghfetch import config


# terminals known to support the kitty graphics protocol
_KITTY_TERMS = {
    "TERM": {"xterm-kitty"},
    "TERM_PROGRAM": {"ghostty", "WezTerm", "Konsole"},
}


def _install_chafa() -> bool:
    """Attempt to install chafa using the system package manager."""
    managers = [
        ("pacman", ["sudo", "pacman", "-S", "--noconfirm", "chafa"]),
        ("apt", ["sudo", "apt", "install", "-y", "chafa"]),
        ("dnf", ["sudo", "dnf", "install", "-y", "chafa"]),
        ("zypper", ["sudo", "zypper", "install", "-y", "chafa"]),
        ("brew", ["brew", "install", "chafa"]),
        ("nix-env", ["nix-env", "-iA", "nixpkgs.chafa"]),
    ]

    for binary, cmd in managers:
        if shutil.which(binary):
            click.echo(f"Installing chafa via {binary}...")
            try:
                result = subprocess.run(cmd)
                if result.returncode == 0 and shutil.which("chafa"):
                    return True
            except Exception:
                pass

    return False


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
    """
    term = os.environ.get("TERM", "")
    term_pgm = os.environ.get("TERM_PROGRAM", "")

    if term in _KITTY_TERMS["TERM"]:
        return "kitty", f"detected Kitty terminal (TERM={term})"

    if term_pgm in _KITTY_TERMS["TERM_PROGRAM"]:
        return "kitty", f"detected {term_pgm} (TERM_PROGRAM={term_pgm})"

    detected = term_pgm or term or "unknown terminal"
    return "chafa", f"{detected} does not support the kitty graphics protocol"


def _set_renderer(renderer: str) -> None:
    """Persist image_renderer into the display section of the config."""
    cfg = config.get_config()
    cfg["display"]["image_renderer"] = renderer
    config._write(cfg)


@click.command()
def auth():
    """Authenticate ghfetch with your GitHub account."""

    click.echo("GitHub API Authentication Setup")
    click.echo()
    click.echo("To get your GitHub Personal Access Token (PAT):")
    click.echo("1. Go to: https://github.com/settings/tokens")
    click.echo("2. Log in with your GitHub account")
    click.echo("3. Click 'Generate new token (classic)'")
    click.echo("4. Give the token a descriptive name (e.g. 'ghfetch')")
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

    if shutil.which("chafa") is None:
        click.echo("chafa is not installed, it's required for avatar rendering.")
        click.echo("Attempting to install it automatically...")
        click.echo()

        if _install_chafa():
            click.echo("✓ chafa installed successfully.")
        else:
            click.echo("✗ Could not install chafa automatically.")
            click.echo("  Install it manually: https://hpjansson.org/chafa/download/")

        click.echo()

    renderer, reason = _detect_renderer()
    _set_renderer(renderer)

    click.echo("Display Setup")

    if renderer == "kitty":
        click.echo(f"✓ Kitty graphics protocol enabled  ({reason})")
    else:
        click.echo(f"✗ Kitty graphics protocol unavailable  ({reason})")
        click.echo("  Your avatar will be rendered as chafa ascii art.")

    click.echo()
    click.echo("You can change this any time by editing:")
    click.echo("  ~/.config/ghfetch/config.json")
    click.echo()
    click.echo("Run 'ghfetch' to view your GitHub stats.")
