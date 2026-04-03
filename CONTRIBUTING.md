# Contributing

Thanks for even considering to contribute to hubfetch!

## Dev Setup

- Python 3.14+
- A GitHub Personal Access Token (needed to actually run the tool during development)
- [chafa](https://hpjansson.org/chafa/) installed for testing image rendering fallback

This project uses [uv](https://github.com/astral-sh/uv) as its package manager. After installing uv, run:

```bash
uv sync
```

This picks up all required dependencies from the lock file. To run the tool locally during development:

```bash
uv run hubfetch
```

## Quality Assurance

Before opening a PR:

- Run unit tests:

```bash
uv run pytest
```

- Format the codebase with Ruff:

```bash
uv run ruff format .
```

- Lint the codebase:

```bash
uv run ruff check .
```

- Keep functions small and documented with docstrings.
- If your change touches the GitHub API integration, make sure it works with both authenticated and unauthenticated states.

## Building Locally

To test the PyInstaller binary build locally:

```bash
uv run pyinstaller hubfetch.spec
./dist/hubfetch
```

## Packaging

This project is **NOT A MONO-REPO**

Packaging files are mirrored under `contrib/` for reference only. The canonical sources are:

| Package Manager | Canonical Source |
|---|---|
| Homebrew | [`PranavU-Coder/homebrew-tap`](https://github.com/PranavU-Coder/homebrew-tap) |
| AUR | `ssh://aur@aur.archlinux.org/hubfetch.git` |
| Scoop | [`PranavU-Coder/scoop-bucket`](https://github.com/PranavU-Coder/scoop-bucket) |

If you're fixing a packaging issue, open the PR in the appropriate repo above, not here.

## Reporting Issues

When reporting an issue, please include:

- OS + Python version
- Terminal emulator (matters for kitty graphics protocol support)
- The exact command you ran
- The full error output or a screenshot of the terminal
