import discord
from discord.ext import commands

import json
import random
import datetime
import re


class Misc(commands.Cog):
    def __init__(self, bot):
        self.__bot = bot
        self.eight_ball_options = []

    async def cog_load(self):
        await super().cog_load()
        print("Misc(bbq23, java, sync) Cog loaded.")

    async def load_data(self):
        with open("data/8ball.json") as f:
            data = json.load(f)
            self.eight_ball_options = data["options"]

    @commands.command(name="bbq23")
    async def bbq23(self, ctx):
        embed = discord.Embed(
            title="BBQ 23",
            color=3447003,
            description="Here's a bunch of gigachads together",
        )
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/968245983697842196/1101298256459346000/IMG_2316.jpg"
        )
        await ctx.send(embed=embed)

    @commands.command(name="beach")
    async def beach(self, ctx):
        embed = discord.Embed(
            title="beach",
            color=3447003,
            description="the sun can't outshine my despair",
        )
        embed.set_image(
            url="https://images-ext-2.discordapp.net/external/cZLn5SlZBKlFg0XB9XGjo3skYghmOo1HF18rQaV5Kdk/%3Fsize%3D600/https/cdn.discordapp.com/banners/402891511991369740/f685e66edfa9f8477f2d65d6c53dd884.webp?width=1200&height=674"
        )
        await ctx.send(embed=embed)

    @commands.command(name="java")
    async def java(self, ctx):
        embed = discord.Embed(
            title="Java", color=3447003, description="Have you tried Kotlin?"
        )
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/968245983697842196/1101253691392143410/41BDFE8C-2BC0-4E2B-A3C9-539962B71707.jpg"
        )
        await ctx.send(embed=embed)

    @commands.command(name="sync")
    async def sync(self, ctx):
        # commands = self.__bot.tree.get_commands(guild=ctx.guild)
        commands = await self.__bot.tree.sync(guild=ctx.guild)
        print("Sync complete")
        await ctx.send(f"Synced {len(commands)} commands")

    @commands.command(name="8ball")
    async def eight_ball(self, ctx):
        await ctx.send(random.choice(self.eight_ball_options))

    @commands.command(name="zipit")
    async def zip_it(self, ctx, duration=""):
        patterns = {
            "days": {"pattern": r"(\d+)\s*(d|day)s?", "duration": 60 * 24},
            "hours": {"pattern": r"(\d+)\s*(h|hr|hour)s?", "duration": 60},
            "minutes": {"pattern": r"(\d+)\s*(m|min|minute)s?", "duration": 1},
        }

        total_duration = datetime.timedelta()
        for v in patterns.values():
            match = re.search(v["pattern"], duration, re.IGNORECASE)
            if match:
                value = int(match.group(1)) * v["duration"]
                total_duration += datetime.timedelta(minutes=value)

        if total_duration.total_seconds == 0:
            await ctx.send(f"Invalid duration: {duration}")
            return

        try:
            await ctx.author.timeout(total_duration, reason="Self timeout via sherp2.0")
            await ctx.send(f"Timed out {ctx.author.nick}")
        except discord.Forbidden:
            await ctx.send(f"Cannot timeout {ctx.author.nick}: No permission")


async def setup_misc_cog(bot, guilds):
    cog = Misc(bot)
    await cog.load_data()
    await bot.add_cog(cog, guilds=guilds)
