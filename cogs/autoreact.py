import discord
from discord.ext import commands
import json
from datetime import datetime

RATE_LIMIT = 3  # seconds


class AutoReact(commands.GroupCog, name="autoreact"):
    def __init__(self):
        super().__init__()
        self.last_reacted = 0

    async def cog_load(self):
        await super().cog_load()
        print("AutoReact Cog Loaded")  # by jadc

    async def load_data(self):
        with open("data/autoreact.json", "r", encoding="utf-8") as f:
            data = json.load(f)["mappings"]
            self.mappings = {x["target"]: x["reaction"] for x in data}

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author.bot:
            return
        if reaction := self.mappings.get(msg.author.id, None):
            if datetime.now().timestamp() - self.last_reacted > RATE_LIMIT:
                await msg.add_reaction(reaction)
                self.last_reacted = datetime.now().timestamp()


async def setup_autoreact(bot, guilds):
    cog = AutoReact()
    await cog.load_data()
    await bot.add_cog(cog, guilds=guilds)
