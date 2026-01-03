from bs4 import BeautifulSoup
import time
import requests

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

sum: int = 0
follower_count: int = 0

for repo_url in repo_links:
    
    html_text = requests.get(repo_url).text
    soup = BeautifulSoup(html_text, 'lxml')
    
    stars_ele = soup.find('span', {'id': 'repo-stars-counter-star'})
    if stars_ele:
        stars = stars_ele.get_text().strip()
        sum += int(stars)

response = requests.get(profile_url)
soup = BeautifulSoup(response.text, 'lxml')
followers_link = soup.find('a', href=lambda x: x and 'tab=followers' in x)

if followers_link:
    followers_count = followers_link.find('span', class_='text-bold')
    if followers_count:
        follower_count = followers_count.get_text().strip()

print(f"stars: {sum}")
print(f"followers: {follower_count}")
