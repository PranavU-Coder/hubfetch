import sys
import click
from hubfetch import config
from hubfetch.auth import auth
from hubfetch.api import GitHubClient
from hubfetch.display import render


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version="1.0.0")
def cli(ctx):
    """neofetch-style CLI for your GitHub profile."""

    # if a subcommand was invoked (e.g. 'hubfetch auth'), let it handle itself
    if ctx.invoked_subcommand is not None:
        return

    if not config.has_credentials():
        click.echo("No credentials found!")
        click.echo("Run 'hubfetch auth' to set up your GitHub token.")
        sys.exit(1)

    credentials = config.get_credentials()
    client = GitHubClient(credentials["token"])
    stats = client.fetch_stats()
    render(stats)


cli.add_command(auth)
