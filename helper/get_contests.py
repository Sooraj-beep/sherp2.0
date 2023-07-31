from bs4 import BeautifulSoup
import requests
import json

LAST_PAGE = 37 # can change as kattis adds more problems

contests = []

link = f'https://open.kattis.com/problem-sources'
    
r = requests.get(link)

assert(r.status_code == 200)

html = r.content.decode('utf-8')
soup = BeautifulSoup(html, 'html.parser')

for item in soup.tbody.children:
    if str(item)[0] == '<':
        child = BeautifulSoup(str(item), 'html.parser')
        contest = child.a['href'].split('/')[-1]

        assert(contest != '')

        contests.append(contest)

data = {
    "contests": contests
}

with open("../data/contests.json", "w") as f:
    json.dump(data, f)

print("Done importing contests! 🥳")