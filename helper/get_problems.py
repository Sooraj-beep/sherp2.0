from bs4 import BeautifulSoup
import requests
import json

LAST_PAGE = 37 # can change as kattis adds more problems

easy = []
medium = []
hard = []

page = 0

while page < LAST_PAGE:
    print('Got Page:', page)
    if page == 0:
        link = 'https://open.kattis.com/problems?order=-difficulty_category&dir=desc'
    else: 
        link = f'https://open.kattis.com/problems?page={page}&order=-difficulty_category&dir=desc'
        
    r = requests.get(link)

    assert(r.status_code == 200)

    html = r.content.decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    for item in soup.tbody.children:
        if str(item)[0] == '<':
            child = BeautifulSoup(str(item), 'html.parser')
            problem_id = child.a['href'].split('/')[-1]

            assert(problem_id != '')


            if str(child.span.next_sibling).strip() == "Easy":
                easy.append(problem_id)
            elif str(child.span.next_sibling).strip() == "Medium":
                medium.append(problem_id)
            else:
                hard.append(problem_id)
            
    print(f'Easy: {len(easy)}, Medium: {len(medium)}, Hard: {len(hard)}')

    page += 1

data = {
    "easy": easy,
    "medium": medium,
    "hard": hard
}

with open("../data/problems.json", "w") as f:
    json.dump(data, f)
print("Done getting problems! 🥳")