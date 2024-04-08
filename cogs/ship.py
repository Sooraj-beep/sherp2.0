import json

import discord
from discord.ext import commands
from discord import app_commands


class Ship(commands.Cog, name="ship"):
    def __init__(self):
        super().__init__()
        self.thresholds = {}

    async def cog_load(self):
        await super().cog_load()
        print("Ship Cog Loaded")

    async def load_data(self):
        with open("data/ship-thresholds.json", "r", encoding="utf-8") as f:
            self.thresholds = json.load(f)

    def get_slogan(self, compat) -> tuple[str, str]:
        for threshold, data in self.thresholds.items():
            if compat >= int(threshold):
                return data["message"], data["image"]
        return ("", "")

    @app_commands.command(
        name="ship", description="Calculates the compatibility between two people"
    )
    async def ship(
        self,
        intr: discord.Interaction,
        first_user: discord.User,
        second_user: discord.User,
    ):
        if first_user.id == second_user.id:
            await intr.response.send_message("No narcissism allowed.", ephemeral=True)
            return

        compat = (first_user.id + second_user.id) % 101
        slogan, image = self.get_slogan(compat)

        embed = discord.Embed(
            type="rich",
            title=f"{first_user.display_name} and {second_user.display_name} are {compat}% compatible!",
            description=slogan,
        )
        embed.set_thumbnail(url=image)

        await intr.response.send_message(embed=embed)


async def setup_ship(bot, guilds):
    cog = Ship()
    await cog.load_data()
    await bot.add_cog(cog, guilds=guilds)
