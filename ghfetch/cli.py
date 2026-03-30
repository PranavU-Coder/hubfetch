import sys
import click
from ghfetch import config
from ghfetch.auth import auth
from ghfetch.api import GitHubClient
from ghfetch.display import render


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version="0.1.0")
def cli(ctx):
    """neofetch-style CLI for your GitHub profile."""

    # if a subcommand was invoked (e.g. 'ghfetch auth'), let it handle itself, not my problem for now
    if ctx.invoked_subcommand is not None:
        return

    if not config.has_credentials():
        click.echo("No credentials found!")
        click.echo("Run 'ghfetch auth' to set up your GitHub token.")
        sys.exit(1)

    credentials = config.get_credentials()

    client = GitHubClient(credentials["token"])
    stats = client.fetch_stats()
    render(stats)


cli.add_command(auth)
