import random

import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice


class Ship(commands.GroupCog, name="ship"):
    def __init__(self):
        super().__init__()

    async def cog_load(self):
        await super().cog_load()
        print("Ship Cog Loaded")

    @app_commands.command(name="ship", description="Calculates the compatibility between two people")
    async def ship(self, intr: discord.Interaction, userA: discord.User, userB: discord.User):
        await intr.response.send_message(userA.name + " and " + userB.name + " are " + str(random.randint(0, 100)) + "% compatible")


async def setup_ship(bot, guilds):
    cog = Ship()
    await bot.add_cog(cog, guilds=guilds)
