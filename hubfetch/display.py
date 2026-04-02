import sys
import shutil
import subprocess

from rich.columns import Columns
from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()

COLOR_RESET = "\033[0m"
COLOR_WHITE = "\033[37m"


class ImageRenderer:
    """Handles terminal image rendering."""

    def __init__(self, size: int = 40, renderer: str = "auto"):
        self.width = size
        self.height = size // 2
        self.renderer = renderer

    def render_kitty_direct(self, image_path: str) -> bool:
        try:
            result = subprocess.run(
                [
                    "chafa",
                    "--format",
                    "kitty",
                    "--size",
                    f"{self.width}x{self.height}",
                    image_path,
                ],
                stdin=subprocess.DEVNULL,
            )
            return result.returncode == 0
        except Exception:
            return False

    def render(self, image_path: str) -> Text | None:
        """
        Render to Rich Text for side-by-side layout.
        """
        if self.renderer == "none":
            return None

        if shutil.which("chafa"):
            result = self._render_with_chafa(image_path)
            if result:
                return result

        return self._placeholder()

    def _render_with_chafa(self, image_path: str) -> Text | None:
        try:
            result = subprocess.run(
                [
                    "chafa",
                    "--format",
                    "symbols",
                    "--colors",
                    "full",
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
            text = Text.from_ansi(result.stdout)
            text.no_wrap = True
            return text
        except Exception:
            return None

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


def _rich_color_to_ansi(color: str) -> str:
    """Map Rich color name strings to ANSI escape codes."""
    mapping = {
        "bold cyan": "1;36",
        "bold green": "1;32",
        "bold yellow": "1;33",
        "bold magenta": "1;35",
        "bold blue": "1;34",
        "bold red": "1;31",
        "bold white": "1;37",
        "cyan": "36",
        "green": "32",
        "yellow": "33",
        "magenta": "35",
        "blue": "34",
        "red": "31",
        "italic": "3",
        "italic dim": "3;2",
    }
    return mapping.get(color, "37")


def _iter_fields(data: dict, cfg: dict):
    """
    Yields (label, value, color) for every enabled field, in display order.
    """
    display_cfg = cfg.get("display", {})

    show = display_cfg.get(
        "show",
        {
            "bio": True,
            "repositories": True,
            "forks": True,
            "stars": True,
            "starred": True,
            "followers": True,
            "following": True,
            "commits": True,
            "issues": True,
            "prs": True,
            "best_day": True,
            "top_language": True,
        },
    )

    default_colors = {
        "user": "bold cyan",
        "bio": "italic",
        "repositories": "bold green",
        "forks": "bold magenta",
        "stars": "bold yellow",
        "starred": "bold blue",
        "followers": "bold cyan",
        "following": "bold red",
        "commits": "bold green",
        "issues": "bold yellow",
        "prs": "bold magenta",
        "best_day": "bold red",
        "top_language": "bold blue",
    }

    cfg_colors = display_cfg.get("colors", {})
    colors = {
        k: cfg_colors.get(k, default_colors.get(k, "bold white"))
        for k in default_colors
    }

    # user is always shown
    yield "User:", data["user"], colors["user"]

    fields = [
        ("bio", "Bio:", lambda d: d.get("bio") or "No bio"),
        ("repositories", "Repositories:", lambda d: str(d["repositories"])),
        ("forks", "Forks:", lambda d: str(d["forks"])),
        ("stars", "Stars:", lambda d: str(d["stars"])),
        ("starred", "Starred:", lambda d: str(d["starred"])),
        ("followers", "Followers:", lambda d: _format_number(d["followers"])),
        ("following", "Following:", lambda d: _format_number(d["following"])),
        ("commits", "Commits:", lambda d: str(d.get("commits", 0))),
        ("issues", "Issues:", lambda d: str(d.get("issues", 0))),
        ("prs", "Pull Requests:", lambda d: str(d.get("prs", 0))),
        ("best_day", "Most Active Day:", lambda d: d.get("best_day")),
    ]

    for key, label, getter in fields:
        if show.get(key):
            value = getter(data)
            if value:
                yield label, value, colors.get(key, "bold white")

    if show.get("top_language") and data.get("top_language") not in (None, "None"):
        yield (
            "Top Language:",
            data["top_language"],
            colors.get("top_language", "bold white"),
        )


def _build_info_lines(data: dict, cfg: dict) -> list[str]:
    """Plain ANSI strings for kitty cursor-positioned layout."""

    def row(label: str, value: str, color: str) -> str:
        ansi = _rich_color_to_ansi(color)
        return f"\033[1m{label:<16}\033[0m \033[{ansi}m{value}\033[0m"

    return [row(label, value, color) for label, value, color in _iter_fields(data, cfg)]


def _build_info_table(data: dict, cfg: dict) -> Table:
    """Rich Table for standard Columns layout."""
    table = Table(show_header=False, box=None, padding=(0, 1, 0, 3), show_edge=False)
    for label, value, color in _iter_fields(data, cfg):
        table.add_row(label, f"[{color}]{value}[/{color}]")
    return table


def _print_kitty_side_by_side(
    image_path: str, lines: list[str], renderer: ImageRenderer
) -> bool:
    if not renderer.render_kitty_direct(image_path):
        return False

    up_lines = renderer.height - 2
    sys.stdout.write(f"\033[{up_lines}A")
    sys.stdout.flush()

    col = renderer.width + 4

    for line in lines:
        sys.stdout.write(f"\033[{col}G{line}\033[K\n")
    sys.stdout.flush()

    remaining = up_lines - len(lines)
    if remaining > 0:
        sys.stdout.write(f"\033[{remaining}B")
        sys.stdout.flush()

    print()
    return True


def render(data: dict) -> None:
    from hubfetch.cache import avatar_path
    from hubfetch.config import get_config

    cfg = get_config()
    disp_cfg = cfg.get("display", {})

    renderer = ImageRenderer(
        size=disp_cfg.get("image_size", 40),
        renderer=disp_cfg.get("image_renderer", "auto"),
    )

    path = avatar_path(data["user"])

    if renderer.renderer == "none":
        console.print(_build_info_table(data, cfg))
        return

    if renderer.renderer == "kitty" and path.exists():
        if _print_kitty_side_by_side(str(path), _build_info_lines(data, cfg), renderer):
            return
        # kitty failed => fall through to chafa

    avatar = renderer.render(str(path)) if path.exists() else renderer._placeholder()
    console.print(
        Columns(
            [avatar, _build_info_table(data, cfg)],
            equal=False,
            expand=False,
            padding=(0, 2),
        )
    )
