import sys
import json
import subprocess

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.columns import Columns

console = Console()

# loading the json file 

json_filename = sys.stdin.readline().strip()

with open(json_filename, 'r') as f:
    data = json.load(f)

# I might revisit ASCII art in future, it is really difficult to capture the depth of image quite well,
# at this point, I might as well make/get an ASCII-art of GitHub Logo and call it a day.

ascii_art = subprocess.run(
    ['ascii-image-converter', '-d', '40,19', '-C', '-c', f'assets/{data["user"]}.png'],
    capture_output=True,
    text=True
)


logo = Text.from_ansi(ascii_art.stdout)

# output to terminal

info_table = Table(show_header=False, box=None, padding=(0, 1, 0, 3), show_edge=False)

info_table.add_row("User:", f"[bold cyan]{data['user']}[/bold cyan]")
info_table.add_row("Bio:", f"[italic dim]{data['bio'] or 'No bio'}[/italic dim]")
info_table.add_row("Forks:", f"[bold green]{data['forks']}[/bold green]")
info_table.add_row("Repositories:", f"[bold green]{data['repositories']}[/bold green]")
info_table.add_row("Stars:", f"[bold yellow]{data['stars']}[/bold yellow]")
info_table.add_row("Starred:", f"[bold magenta]{data['starred']}[/bold magenta]")
info_table.add_row("Followers:", f"[bold blue]{data['followers']}[/bold blue]")
info_table.add_row("Following:", f"[bold red]{data['following']}[/bold red]")
info_table.add_row("Contributions this year:", f"[bold white]{data['contributions']}[/bold white]")

columns = Columns([logo, info_table], equal=False, expand=False, padding=(0, 2))
console.print(columns)
