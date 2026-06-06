import discord
from discord.ext import commands

import json
import random


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

    @commands.hybrid_command(name="bbq23", description="Post the BBQ 23 group photo.")
    async def bbq23(self, ctx):
        embed = discord.Embed(
            title="BBQ 23",
            color=3447003,
            description="Here's a bunch of gigachads together",
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/968245983697842196/1101298256459346000/IMG_2316.jpg")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="bbq25", description="Post the BBQ 25 group photo.")
    async def bbq25(self, ctx):
        embed = discord.Embed(
            title="BBQ 25",
            color=3447003,
            description="Here's a bunch of <:OnPhone:1062142401973588039> investors together",
        )
        file = discord.File("attachments/bbq25.jpeg", filename="bbq25.jpeg")
        embed.set_image(url="attachment://bbq25.jpeg")
        await ctx.send(embed=embed, file=file)

    @commands.hybrid_command(name="bbq26", description="Post the BBQ 26 group photo.")
    async def bbq26(self, ctx):
        embed = discord.Embed(
            title="BBQ 26",
            color=3447003,
            description="Here's a bunch of gooners together",
        )
        file = discord.File("attachments/bbq26.jpeg", filename="bbq26.jpeg")
        embed.set_image(url="attachment://bbq26.jpeg")
        await ctx.send(embed=embed, file=file)

    @commands.hybrid_command(name="beach", description="Post the server beach image.")
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

    @commands.hybrid_command(name="java", description="Have you tried Kotlin?")
    async def java(self, ctx):
        embed = discord.Embed(title="Java", color=3447003, description="Have you tried Kotlin?")
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/968245983697842196/1101253691392143410/41BDFE8C-2BC0-4E2B-A3C9-539962B71707.jpg"
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="sync", description="Sync slash commands for this server.")
    async def sync(self, ctx):
        # commands = self.__bot.tree.get_commands(guild=ctx.guild)
        commands = await self.__bot.tree.sync(guild=ctx.guild)
        print("Sync complete")
        await ctx.send(f"Synced {len(commands)} commands")

    @commands.hybrid_command(name="8ball", description="Ask the magic 8 ball.")
    async def eight_ball(self, ctx):
        await ctx.send(random.choice(self.eight_ball_options))


async def setup_misc_cog(bot, guilds):
    cog = Misc(bot)
    await cog.load_data()
    await bot.add_cog(cog, guilds=guilds)
