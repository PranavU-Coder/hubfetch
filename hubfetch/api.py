import re
import requests
from concurrent.futures import ThreadPoolExecutor


class GitHubClient:
    """GitHub API client — wraps REST v3 and GraphQL v4 endpoints."""

    BASE_URL = "https://api.github.com"
    GRAPHQL_URL = "https://api.github.com/graphql"

    def __init__(self, token: str) -> None:
        self._token = token
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
            }
        )

    def _get(self, path: str, **params) -> dict:
        response = self._session.get(f"{self.BASE_URL}{path}", params=params)
        response.raise_for_status()
        return response.json()

    def _get_with_headers(self, path: str, **params):
        response = self._session.get(f"{self.BASE_URL}{path}", params=params)
        response.raise_for_status()
        return response.json(), response.headers

    def _graphql(self, query: str, variables: dict) -> dict:
        response = self._session.post(
            self.GRAPHQL_URL,
            json={"query": query, "variables": variables},
        )
        response.raise_for_status()
        return response.json()

    def get_user(self) -> dict:
        return self._get("/user")

    def get_repos(self, username: str) -> list[dict]:
        repos = []
        page = 1
        while True:
            page_data = self._get(
                f"/users/{username}/repos",
                per_page=100,
                page=page,
            )
            if not page_data:
                break
            repos.extend(page_data)
            page += 1
        return repos

    def get_starred_count(self, username: str) -> int:
        _, headers = self._get_with_headers(
            f"/users/{username}/starred",
            per_page=1,
        )
        if "Link" in headers:
            match = re.search(r'page=(\d+)>; rel="last"', headers["Link"])
            if match:
                return int(match.group(1))
        data, _ = self._get_with_headers(f"/users/{username}/starred", per_page=100)
        return len(data)

    def get_contributions(self, username: str, year: int) -> dict:
        query = """
        query($login: String!, $from: DateTime!, $to: DateTime!) {
            user(login: $login) {
                contributionsCollection(from: $from, to: $to) {
                    totalCommitContributions
                    totalIssueContributions
                    totalPullRequestContributions
                    contributionCalendar {
                        totalContributions
                        weeks {
                            contributionDays {
                                date
                                contributionCount
                            }
                        }
                    }
                }
            }
        }
        """
        variables = {
            "login": username,
            "from": f"{year}-01-01T00:00:00Z",
            "to": f"{year}-12-31T23:59:59Z",
        }
        data = self._graphql(query, variables)
        collection = data["data"]["user"]["contributionsCollection"]
        calendar = collection["contributionCalendar"]

        days = [
            day
            for week in calendar.get("weeks", [])
            for day in week.get("contributionDays", [])
        ]
        best = max(
            days,
            key=lambda d: d["contributionCount"],
            default={"date": "None", "contributionCount": 0},
        )
        best_count = best["contributionCount"]

        return {
            "commits": collection.get("totalCommitContributions", 0),
            "issues": collection.get("totalIssueContributions", 0),
            "prs": collection.get("totalPullRequestContributions", 0),
            "best_day": f"{best_count}",
        }

    def fetch_stats(self, year: int = 2026) -> dict:
        from hubfetch.cache import ensure_avatar, get_cached_stats, save_stats

        cached = get_cached_stats()
        if cached:
            ensure_avatar(cached["user"], "")
            return cached

        user = self.get_user()
        username = user["login"]
        avatar_url = user.get("avatar_url", "")

        with ThreadPoolExecutor(max_workers=4) as pool:
            future_repos = pool.submit(self.get_repos, username)
            future_starred = pool.submit(self.get_starred_count, username)
            future_contribs = pool.submit(self.get_contributions, username, year)
            future_avatar = pool.submit(ensure_avatar, username, avatar_url)

            repos = future_repos.result()
            starred = future_starred.result()
            contribs = future_contribs.result()
            future_avatar.result()

        sum_stars = sum(r.get("stargazers_count", 0) for r in repos)
        fork_count = sum(1 for r in repos if r.get("fork", False))

        languages = {}
        for r in repos:
            lang = r.get("language")
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
        top_language = max(languages, key=languages.get) if languages else "None"

        stats = {
            "user": username,
            "bio": user.get("bio") or "No bio available",
            "repositories": user.get("public_repos", 0),
            "forks": fork_count,
            "stars": sum_stars,
            "starred": starred,
            "followers": user.get("followers", 0),
            "following": user.get("following", 0),
            "commits": contribs.get("commits", 0),
            "issues": contribs.get("issues", 0),
            "prs": contribs.get("prs", 0),
            "best_day": contribs.get("best_day"),
            "top_language": top_language,
        }

        save_stats(stats)
        return stats
