import discord
from discord.ext import commands

class Misc(commands.Cog):

    def __init__(self, bot):
        self.__bot = bot

    async def cog_load(self):
        await super().cog_load()
        print("Misc(bbq23, java, sync) Cog loaded.")

    @commands.command(name="bbq23")
    async def bbq23(self, ctx):
        embed = discord.Embed(title="BBQ 23",color=3447003,description="Here's a bunch of gigachads together")
        embed.set_image(url="https://cdn.discordapp.com/attachments/968245983697842196/1101298256459346000/IMG_2316.jpg")
        await ctx.send(embed=embed)

    @commands.command(name="java")
    async def java(self, ctx):
        embed = discord.Embed(title="Java",color = 3447003,description="Have you tried Kotlin?")
        embed.set_image(url="https://cdn.discordapp.com/attachments/968245983697842196/1101253691392143410/41BDFE8C-2BC0-4E2B-A3C9-539962B71707.jpg")
        await ctx.send(embed=embed)

    @commands.command(name="sync")
    async def sync(self, ctx):
        # commands = self.__bot.tree.get_commands(guild=ctx.guild)
        commands = await self.__bot.tree.sync(guild=ctx.guild)
        print("Sync complete")
        await ctx.send(f"Synced {len(commands)} commands")

async def setup_misc_cog(bot, guilds):
    cog = Misc(bot)
    await bot.add_cog(cog, guilds=guilds)
