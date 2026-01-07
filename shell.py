import json
import subprocess

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.columns import Columns

console = Console()

# loading the json file 

with open('output/PranavU-Coder_stats.json', 'r') as f:  
    data = json.load(f)

# generating ASCII art through chafa 

chafa = subprocess.run(
    ['chafa', '-f', 'symbols', '--size', '25x12', '--colors', '256', 'assets/pfp.png'],
    capture_output=True,
    text=True
)

logo = Text.from_ansi(chafa.stdout)

# output to terminal

info_table = Table(show_header=False, box=None, padding=(0, 1, 0, 3), show_edge=False)
info_table.add_row("User:", f"[bold cyan]{data['user']}[/bold cyan]")
info_table.add_row("Repositories:", f"[bold green]{data['repositories']}[/bold green]")
info_table.add_row("Stars:", f"[bold yellow]{data['stars']}[/bold yellow]")
info_table.add_row("Starred:", f"[bold magenta]{data['starred']}[/bold magenta]")
info_table.add_row("Followers:", f"[bold blue]{data['followers']}[/bold blue]")
info_table.add_row("Following:", f"[bold red]{data['following']}[/bold red]")
info_table.add_row("Timezone:", f"[bold white]{data['timezone']}[/bold white]")

columns = Columns([logo, info_table], equal=False, expand=False, padding=(0, 2))
console.print(columns)
