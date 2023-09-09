# import random
# import json
import pandas as pd

import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
from cogs.helpers.gspread_client import get_sheet


class Faq(commands.GroupCog, name="faq"):
    def __init__(self):
        self.faq_sheet = None

    async def cog_load(self):
        await super().cog_load()
        print("faq Cog Loaded")

    async def load_sheet(self):
        self.faq_sheet = await get_sheet()

    @app_commands.command(
        name="list", description="view everything in the faq sheet"
    )
    async def list(self, intr: discord.Interaction):
        data = self.faq_sheet.get_all_records()
        df = pd.DataFrame(data)

        # make an embed with bolded question followed by (prefix: prefix) and in newline plain text the answer
        embed = discord.Embed(title="Frequently Asked Questions", color=0x00ff00)
        for index, row in df.iterrows():
            header = "**" + row['Question'] + "**" + " (prefix: " + row['Prefix'] + ")"
            embed.add_field(name=header, value=row['Answer'], inline=False)
        await intr.response.send_message(embed=embed)

async def setup_faq(bot, guilds):
    cog = Faq()
    await cog.load_sheet()
    await bot.add_cog(cog, guilds=guilds)
