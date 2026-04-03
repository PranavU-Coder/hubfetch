import sys
import click
import requests
from importlib.metadata import version
from hubfetch import config
from hubfetch.auth import auth, _detect_renderer, _ensure_chafa
from hubfetch.api import GitHubClient
from hubfetch.display import render


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version=version("hubfetch"))
def cli(ctx):
    """neofetch-style CLI for your GitHub profile."""

    # if a subcommand was invoked (e.g. 'hubfetch auth'), let it handle itself
    if ctx.invoked_subcommand is not None:
        return

    if not config.has_credentials():
        click.echo("No credentials found!")
        click.echo("Run 'hubfetch auth' to set up your GitHub token.")
        sys.exit(1)

    # ensure chafa is available before rendering if not on a kitty terminal
    renderer, _ = _detect_renderer()
    if renderer == "chafa":
        _ensure_chafa()

    credentials = config.get_credentials()
    client = GitHubClient(credentials["token"])

    try:
        stats = client.fetch_stats()
    except RuntimeError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except requests.HTTPError as e:
        click.echo(f"GitHub API error: {e}", err=True)
        sys.exit(1)

    render(stats)


cli.add_command(auth)
