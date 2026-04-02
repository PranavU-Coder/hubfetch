# hubfetch

![banner](assets/banner.png)

## Description

A [not very minimal] fetching tool for your GitHub profile. Flex at your friends from terminal itself without even opening a new tab.

This entire script is written purely in python and uses GitHub's REST API for acquiring details of your profile, you can opt out of certain fields and even change the image rendered in accordance to your needs by editing at ~/.config/hubfetch.json

The image rendered depends heavily on the terminal as it requires kitty's graphics protocol and full image rendering is supported in those terminals which are capable enough of supporting it.

Don't worry if your favorite terminal doesn't support kitty's graphics protocol as the script downloads [chafa](https://hpjansson.org/chafa/) as fallback to display your profile picture in ASCII-block art format.

### Terminals Supporting Kitty's Graphics Protocol

* **[Kitty](https://sw.kovidgoyal.net/kitty/)** (Native support)
* **[WezTerm](https://wezfurlong.org/wezterm/)**
* **[Ghostty](https://ghostty.org/)**
* **[Konsole](https://konsole.kde.org/)** (KDE's default terminal)

## Previews

<details>
<summary>First Time Installation & Kitty/Non-Kitty Looks</summary>

![Alt](./assets/preview-1.png)
![Alt](./assets/preview-2.png)
![Alt](./assets/config.png)

https://github.com/user-attachments/assets/9d06be44-fa36-4e24-bdee-a29838a801c3

</details>

## Features

* **Comprehensive GitHub Stats**: Fetches real-time (ok maybe not that real-time, there is caching of data that is maintained each hour) data  including repositories, total stars, forks, followers, and following count.
* **Contribution Tracking**: Displays your total commits, open issues, and pull requests from the current year using GitHub's GraphQL API.
* **Image Rendering**: 
    * **High-Res:** Utilizes the Kitty graphics protocol for native, high-resolution avatar rendering.
    * **Legacy/Fallback:** Automatically detects terminal capabilities and falls back to `chafa` for high-quality ANSI symbols/block art.
* **Caching**: 
    * **Avatar Cache:** Refreshes your profile picture every 6 hours.
    * **Stats Cache:** Keeps your GitHub data fresh with a 1-hour expiration to minimize API calls and maximizes speed.
* **Dynamic Customization**: Fully configurable via `~/.config/hubfetch/config.json` as discussed earlier. Toggle individual fields, adjust image dimensions, or customize the entire color palette with bold and italic Rich styles.
* **Secure Authentication**: Dedicated `auth` command to securely handle GitHub Personal Access Tokens (PAT) and verify credentials before setup.
* **Modern CLI Experience** – Built with `Click` for a seamless command-line interface and `Rich` for beautiful, side-by-side terminal layouts.

## Installation

[WIP]

## Tech Stack

[![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Click](https://img.shields.io/badge/Click-CLI-000000?style=for-the-badge&logo=flask&logoColor=white)](https://click.palletsprojects.com/)
[![Rich](https://img.shields.io/badge/Rich-Terminal_UI-8A2BE2?style=for-the-badge&logo=python&logoColor=white)](https://rich.readthedocs.io/)
[![Requests](https://img.shields.io/badge/Requests-HTTP-0052CC?style=for-the-badge&logo=python&logoColor=white)](https://requests.readthedocs.io/)
[![Chafa](https://img.shields.io/badge/Chafa-Terminal_Art-FF4500?style=for-the-badge&logo=gnu&logoColor=white)](https://hpjansson.org/chafa/)
[![UV](https://img.shields.io/badge/Package_Manager-UV-8A2BE2?style=for-the-badge&logo=astral&logoColor=white)](https://github.com/astral-sh/uv)
[![Hatchling](https://img.shields.io/badge/Build-Hatchling-4B8BBE?style=for-the-badge&logo=python&logoColor=white)](https://hatch.pypa.io/)
[![Ruff](https://img.shields.io/badge/Linter-Ruff-D7FF64?style=for-the-badge&logo=ruff&logoColor=black)](https://github.com/astral-sh/ruff)
[![Pytest](https://img.shields.io/badge/Testing-Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://docs.pytest.org/)

## Future

Discussed in [[placeholder text till I make it public]]

All features/bug-fixes being implemented can be visible in the [roadmap](https://github.com/users/PranavU-Coder/projects/11)

A rich issue-template to raise all required changes.

## License

[MIT](https://github.com/PranavU-Coder/hubfetch?tab=MIT-1-ov-file)

## Other

<a href="https://star-history.com/#PranavU-Coder/hubfetch&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=PranavU-Coder/hubfetch&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=PranavU-Coder/hubfetch&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=PranavU-Coder/hubfetch&type=Date" />
 </picture>
</a>
