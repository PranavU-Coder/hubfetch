import shutil
import subprocess

from pathlib import Path

from PIL import Image
from rich.columns import Columns
from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()

COLOR_RESET = "\033[0m"
COLOR_RED = "\033[31m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_BLUE = "\033[34m"
COLOR_PURPLE = "\033[35m"
COLOR_CYAN = "\033[36m"
COLOR_WHITE = "\033[37m"
COLOR_BOLD = "\033[1m"


class ImageRenderer:
    """Handles terminal image rendering"""

    def __init__(self, size: int = 40):
        self.width = size
        self.height = size // 2

    def render(self, image_path: str) -> Text:
        """Convert a local image file into a Rich Text object of terminal art."""

        if self._is_ascii_image_converter_available():
            result = self._render_with_ascii_image_converter(image_path)
            if result:
                return result

        if self._is_chafa_available():
            result = self._render_with_chafa(image_path)
            if result:
                return result

        return self._render_block_art(image_path)

    def _is_chafa_available(self) -> bool:
        return shutil.which("chafa") is not None

    def _is_ascii_image_converter_available(self) -> bool:
        return shutil.which("ascii-image-converter") is not None

    def _render_with_ascii_image_converter(self, image_path: str) -> Text | None:
        try:
            result = subprocess.run(
                [
                    "ascii-image-converter",
                    "-d",
                    f"{self.width},{self.height}",
                    "-C",
                    "-c",
                    image_path,
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                return None
            return Text.from_ansi(result.stdout)
        except Exception:
            return None

    def _render_with_chafa(self, image_path: str) -> Text | None:
        try:
            result = subprocess.run(
                [
                    "chafa",
                    "--size",
                    f"{self.width}x{self.height}",
                    "--dither",
                    "ordered",
                    image_path,
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                return None
            return Text.from_ansi(result.stdout)
        except Exception:
            return None

    def _render_block_art(self, image_path: str) -> Text:
        try:
            img = (
                Image.open(image_path)
                .convert("RGB")
                .resize((self.width // 2, self.height))
            )
            lines = []
            for y in range(img.height):
                line = " "
                for x in range(img.width):
                    r, g, b = img.getpixel((x, y))
                    line += f"\033[48;2;{r};{g};{b}m  {COLOR_RESET}"
                lines.append(line)
            return Text.from_ansi("\n".join(lines))
        except Exception:
            return self._placeholder()

    def _placeholder(self) -> Text:
        lines = [
            f" {COLOR_WHITE}┌───────────────────────────────┐{COLOR_RESET}",
            f" {COLOR_WHITE}│                               │{COLOR_RESET}",
            f" {COLOR_WHITE}│                               │{COLOR_RESET}",
            f" {COLOR_WHITE}│         NO AVATAR             │{COLOR_RESET}",
            f" {COLOR_WHITE}│         AVAILABLE             │{COLOR_RESET}",
            f" {COLOR_WHITE}│                               │{COLOR_RESET}",
            f" {COLOR_WHITE}│                               │{COLOR_RESET}",
            f" {COLOR_WHITE}└───────────────────────────────┘{COLOR_RESET}",
        ]
        return Text.from_ansi("\n".join(lines))


def _format_number(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def _build_info_table(data: dict) -> Table:
    table = Table(show_header=False, box=None, padding=(0, 1, 0, 3), show_edge=False)

    table.add_row("User:", f"[bold cyan]{data['user']}[/bold cyan]")
    table.add_row("Bio:", f"[italic dim]{data['bio'] or 'No bio'}[/italic dim]")
    table.add_row("Repositories:", f"[bold green]{data['repositories']}[/bold green]")
    table.add_row("Forks:", f"[bold green]{data['forks']}[/bold green]")
    table.add_row("Stars:", f"[bold yellow]{data['stars']}[/bold yellow]")
    table.add_row("Starred:", f"[bold magenta]{data['starred']}[/bold magenta]")
    table.add_row(
        "Followers:", f"[bold blue]{_format_number(data['followers'])}[/bold blue]"
    )
    table.add_row(
        "Following:", f"[bold red]{_format_number(data['following'])}[/bold red]"
    )
    table.add_row(
        "Contributions:",
        f"[bold white]{data['contributions']} this year[/bold white]",
    )

    return table


def render(data: dict) -> None:
    from ghfetch.cache import (
        avatar_path,
    )  # another banger of a local import by sir Pranhub

    renderer = ImageRenderer(size=40)

    path = avatar_path(data["user"])
    if path.exists():
        avatar = renderer.render(str(path))
    else:
        avatar = renderer._placeholder()

    info_table = _build_info_table(data)
    console.print(
        Columns([avatar, info_table], equal=False, expand=False, padding=(0, 2))
    )
