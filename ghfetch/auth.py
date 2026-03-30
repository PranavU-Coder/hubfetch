import sys
import click
import requests
from ghfetch import config


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

    if config.set_credentials(token, username):
        click.echo(f"Authenticated as: {username}")
        click.echo("Token saved successfully!")
        click.echo()
        click.echo("Run 'ghfetch' to view your GitHub stats.")
    else:
        click.echo("Failed to save credentials.", err=True)
        sys.exit(1)
