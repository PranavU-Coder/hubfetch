import requests
from datetime import datetime, timezone as tz, timedelta
import re
import json
import sys

# rewriting it with the official GitHub REST API instead of webscraping using bs4

# I am not exposing my GitHub-Token for public :p

GITHUB_TOKEN = ""

gh_username = sys.stdin.readline().strip()

headers = {
    'Accept': 'application/vnd.github+json'
}

if GITHUB_TOKEN:
    headers['Authorization'] = f'Bearer {GITHUB_TOKEN}'

user_url = f"https://api.github.com/users/{gh_username}"
user_response = requests.get(user_url, headers=headers)

if user_response.status_code != 200:
    print(f"error: {user_response.status_code}")
    print(user_response.json())
    exit(1)

user_data = user_response.json()

# all attributes I want to extract.

sum_stars: int = 0
repositories: int = 0
follower_count: int = 0
following_count: int = 0
contributions_this_year: int = 0
sum_starred: int = 0
bio: str = ""
fork_count: int = 0 

# This can be derived directly from the API 

follower_count = user_data.get('followers', 0)
following_count = user_data.get('following', 0)
repositories = user_data.get('public_repos', 0)
bio = user_data.get('bio', 'No bio available')

# I need this for getting the GitHub pfp of the user 

avatar_url = user_data.get('avatar_url')

if avatar_url:
    avatar_response = requests.get(avatar_url)
    
    if avatar_response.status_code == 200:
        avatar_path = f'assets/{gh_username}.png'
        with open(avatar_path, 'wb') as f:
            f.write(avatar_response.content)

# supporting pagination

repos = []
page = 1

while True:
    repos_url = f"https://api.github.com/users/{gh_username}/repos?per_page=100&page={page}"
    repos_response = requests.get(repos_url, headers=headers)
    page_repos = repos_response.json()

    if not page_repos:
        break

    for repo in page_repos:
        sum_stars += repo.get('stargazers_count', 0)
        if repo.get('fork', False):
            fork_count += 1

    page += 1

starred_url = f"https://api.github.com/users/{gh_username}/starred?per_page=1"
starred_response = requests.get(starred_url, headers=headers)

if 'Link' in starred_response.headers:
    link_header = starred_response.headers['Link']
    match = re.search(r'page=(\d+)>; rel="last"', link_header)
    sum_starred = int(match.group(1)) if match else len(starred_response.json())
else:
    sum_starred = len(starred_response.json())

# using GraphQL to get contributions made by user this particular year.

if GITHUB_TOKEN:
    query = """
    query($username: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $username) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            totalContributions
          }
        }
      }
    }
    """
    
    variables = {
        "username": gh_username,
        "from": "2026-01-01T00:00:00Z",
        "to": "2026-12-31T23:59:59Z"
    }
    
    graphql_headers = headers.copy()
    graphql_headers['Content-Type'] = 'application/json'
    
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": variables},
        headers=graphql_headers
    )
    
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and data['data']['user']:
            contributions_this_year = data['data']['user']['contributionsCollection']['contributionCalendar']['totalContributions']
    else:
        print(f"GraphQL Error: {response.json()}")
else:
    print("warning: GITHUB_TOKEN not set, contributions count unavailable till set.")


# metrics I want to return to the end-user

stats = {
    'user': gh_username,
    'bio': bio,
    'repositories': repositories,
    'forks': fork_count,
    'stars': sum_stars,
    'starred': sum_starred,
    'followers': follower_count,
    'following': following_count,
    'contributions': contributions_this_year
}

# since most features work properly it's time to output this in a file so I can extract info for CLI 

with open(f'output/{gh_username}_stats.json', 'w') as f:
    json.dump(stats, f, indent=2)
