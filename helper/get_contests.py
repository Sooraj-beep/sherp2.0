import bs4
from bs4 import BeautifulSoup
from aiohttp import ClientSession
import asyncio
import json

async def get_contests():
    http = ClientSession()
    contests = []

    async with http.get("https://open.kattis.com/problem-sources") as resp:
        assert resp.status == 200

        html = await resp.text(encoding="utf-8")
        soup = BeautifulSoup(html, "html.parser")

        for item in soup.tbody.children:
            if not type(item) is bs4.element.Tag:
                continue
            contest = item.a["href"].split("/")[-1]
            assert contest

            contests.append(contest)

    data = {"contests": contests}
    with open("../data/contests.json", "w") as f:
        json.dump(data, f)

    print("Done importing contests!")
    await http.close()

asyncio.run(get_contests())