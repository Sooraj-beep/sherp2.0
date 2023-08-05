import random
import json

import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice

class Kattis(commands.GroupCog, name="kattis"):
    def __init__(self):
        self.book_url = ""
        self.easy_problems = []
        self.medium_problems = []
        self.hard_problems = []
        self.all_problems = []
        self.specific_problems = {}

    async def cog_load(self):
        await super().cog_load()
        print("Kattis Cog Loaded")

    async def load_data(self):
        with open("data/kattis.json", "r", encoding='utf-8') as f:
            self.book_url = json.load(f)["book"]

        with open("data/problems.json", "r", encoding='utf-8') as f:
            problems = json.load(f)
            self.easy_problems = problems["easy"]
            self.medium_problems = problems["medium"]
            self.hard_problems = problems["hard"]
            self.all_problems = self.easy_problems + self.medium_problems + self.hard_problems

        with open("data/specific.json", "r", encoding='utf-8') as f:
            self.specific_problems = json.load(f)

    def get_kattis_url(self, problem):
        return f"https://open.kattis.com/problems/{problem}"

    @app_commands.command(name="book", description="Get the url to a random google sheets document idk.")
    async def book(self, intr: discord.Interaction):
        await intr.response.send_message(self.book_url)

    @app_commands.command(name="problem", description="Get a random kattis problem based on the chosen difficulty.")
    @app_commands.describe(difficulty="Prolem difficulty")
    @app_commands.choices(difficulty=[
        Choice(name="easy", value=0),
        Choice(name="medium", value=1),
        Choice(name="hard", value=2),
        Choice(name="any", value=3)])
    async def problem(self, intr: discord.Interaction, difficulty: Choice[int]):
        problem = ""
        match difficulty.value:
            case 0:
                problem = random.choice(self.easy_problems)
            case 1:
                problem = random.choice(self.medium_problems)
            case 2:
                problem = random.choice(self.hard_problems)
            case 3:
                problem = random.choice(self.all_problems)
            case _ :
                await intr.response.send_message("Invalid problem difficulty")
                return
        
        await intr.response.send_message(self.get_kattis_url(problem))

    @app_commands.command(name="by-category", description="Get a random kattis problem based on the chosen category.")
    @app_commands.describe(category="Prolem category like dp, graph etc")
    async def by_category(self, intr: discord.Interaction, category: str):
        if category not in self.specific_problems:
            reply = "No problem from this category found!\nTry one of these categories instead:\n"
            for k in self.specific_problems:
                reply += f"{k}\n"
            await intr.response.send_message(reply)
            return
        
        problem = random.choice(self.specific_problems[category])
        await intr.response.send_message(self.get_kattis_url(problem))


    @app_commands.command(name="rank", description="Get the url to the kattis ranklist")
    async def rank(self, intr: discord.Interaction):
        await intr.response.send_message("https://open.kattis.com/ranklist")

    @app_commands.command(name="contests", description="Get a list of kattis contests")
    async def contests(self, intr: discord.Interaction):
        await intr.response.send_message("https://open.kattis.com/problem-sources/")

async def setup_kattis(bot, guilds):
    cog = Kattis()
    await cog.load_data()
    await bot.add_cog(cog, guilds=guilds)
