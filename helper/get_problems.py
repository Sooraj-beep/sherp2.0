import bs4
from bs4 import BeautifulSoup
from aiohttp import ClientSession
import asyncio
import json

LAST_PAGE = 37  # can change as kattis adds more problems


async def get_problems():
    easy = []
    medium = []
    hard = []
    http = ClientSession()

    params = {"order": "-difficulty_category", "dir": "desc"}
    for page in range(LAST_PAGE):
        print("Got page:", page)
        params["page"] = page
        async with http.get("https://open.kattis.com/problems", params=params) as resp:
            assert resp.status == 200, "Kattis responsed with non 200 status code!"
            html = await resp.text(encoding="utf-8")
            soup = BeautifulSoup(html, "html.parser")

            for item in soup.tbody.children:
                if not type(item) is bs4.element.Tag:
                    continue
                problem_id = item.a["href"].split("/")[-1]
                assert problem_id, "Problem ID not valid"

                match item.span.next_sibling.strip():
                    case "Easy":
                        easy.append(problem_id)
                    case "Medium":
                        medium.append(problem_id)
                    case "Hard":
                        hard.append(problem_id)
                    case _:
                        assert False, "Unknown problem difficulty"
        asyncio.sleep(3)

    print(f"Easy: {len(easy)}, Medium: {len(medium)}, Hard: {len(hard)}")
    data = {"easy": easy, "medium": medium, "hard": hard}
    with open("../data/problems.json", "w") as f:
        json.dump(data, f)
    print("Done getting problems!")
    await http.close()


asyncio.run(get_problems())
