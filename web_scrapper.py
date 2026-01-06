from bs4 import BeautifulSoup
import time
import requests
from datetime import datetime, timezone as tz, timedelta

gh_username = input("Enter your GitHub username: ")
profile_url = f"https://github.com/{gh_username}"
repo_links = []

# to support pagination
page = 1

while True:
    url = f"https://github.com/{gh_username}?page={page}&tab=repositories"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    
    repos = soup.find_all('a', {'itemprop': 'name codeRepository'})
    
    if not repos:
        break
    
    for repo in repos:
        repo_path = repo.get('href')
        repo_links.append(f"https://github.com{repo_path}")
    
    page += 1

# all attributes I want to extract.

sum_stars: int = 0
repositories: int = 0
follower_count: int = 0
following_count: int = 0
# contributions_this_year: int = 0
# contributions_since_last_year: int = 0
timezone: str = 'Not set'
sum_starred: int = 0

for repo_url in repo_links:
    
    html_text = requests.get(repo_url).text
    soup = BeautifulSoup(html_text, 'lxml')
    
    stars_ele = soup.find('span', {'id': 'repo-stars-counter-star'})
    if stars_ele:
        stars = stars_ele.get_text().strip()
        sum_stars += int(stars)

repositories = len(repo_links)

response = requests.get(profile_url)
soup = BeautifulSoup(response.text, 'lxml')

followers_link = soup.find('a', href=lambda x: x and 'tab=followers' in x)
following_link = soup.find('a', href=lambda x: x and 'tab=following' in x)

if followers_link:
    followers_count = followers_link.find('span', class_='text-bold')
    if followers_count:
        follower_count = followers_count.get_text().strip()

if following_link:
    following_count_ele = following_link.find('span', class_='text-bold')
    if following_count_ele:
        following_count = following_count_ele.get_text().strip()

stars_link = soup.find('a', href=lambda x: x and 'tab=stars' in x)
if stars_link:
    stars_counter = stars_link.find('span', class_='Counter')
    if stars_counter:
        sum_starred = stars_counter.get_text().strip()

# content is dynamically rendered hence this is actually a bit hard to extract normally.

timezone_ele = soup.find('profile-timezone')
if timezone_ele:
    hours_ahead = timezone_ele.get('data-hours-ahead-of-utc', '')

    if hours_ahead:
        hours = float(hours_ahead)
        sign = '+' if hours >= 0 else '-'
        hours_int = int(abs(hours))
        minutes = int((abs(hours) - hours_int) * 60)

        utc_now = datetime.now(tz.utc)
        user_tz = tz(timedelta(hours=hours))
        user_time = utc_now.astimezone(user_tz)
        current_time = user_time.strftime('%H:%M')

        timezone = f"{current_time} (UTC {sign}{hours_int:02d}:{minutes:02d})"

# metrics I want to return to the end-user

print("\n")
print(f"user: {gh_username}")
print(f"public-repositories: {repositories}")
print(f"stars: {sum_stars}")
print(f"starred: {sum_starred}")
print(f"followers: {follower_count}")
print(f"following: {following_count}")
print(f"timezone: {timezone}")
