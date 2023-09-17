import pandas as pd
import discord
from discord.ext import commands
from discord import app_commands
from cogs.helpers.gspread_client import get_sheet
from helper import get_config


__cfg = get_config().get("faq", None)

ADMIN_ROLE = (
    __cfg.get("admin_role_name") if __cfg else "mod"
)

class Faq(commands.GroupCog, name="faq"):
    def __init__(self):
        self.faq_sheet = None

    async def cog_load(self):
        await super().cog_load()
        print("faq Cog Loaded")

    async def load_sheet(self):
        self.faq_sheet = await get_sheet()
    
    def isAdmin(self, user):
        mod_role = discord.utils.get(user.guild.roles, name=ADMIN_ROLE)
        return mod_role in user.roles

    @app_commands.command(
        name="list", description="view everything in the faq sheet"
    )
    async def list(self, intr: discord.Interaction):
        data = self.faq_sheet.get_all_records()
        df = pd.DataFrame(data)
        embed = discord.Embed(title="Frequently Asked Questions", color=0x00ff00)
        for index, row in df.iterrows():
            header = "**" + row['Question'] + "**" + " (prefix: " + row['Prefix'] + ")"
            embed.add_field(name=header, value=row['Answer'], inline=False)
        await intr.response.send_message(embed=embed)

    @app_commands.command(
        name="search", description="search for a question with a prefix"
    )
    @app_commands.describe(prefix="Prefix to search for")
    async def search(self, intr: discord.Interaction, prefix: str):
        data = self.faq_sheet.get_all_records()
        df = pd.DataFrame(data)

        # make an embed with bolded question followed by (prefix: prefix) and in newline plain text the answer
        embed = discord.Embed(title="Frequently Asked Questions", color=0x00ff00)
        for index, row in df.iterrows():
            if row['Prefix'] == prefix:
                header = "**" + row['Question'] + "**" + " (prefix: " + row['Prefix'] + ")"
                embed.add_field(name=header, value=row['Answer'], inline=False)
        # if no questions with that prefix exist, send a message saying so
        if len(embed.fields) == 0:
            await intr.response.send_message("No questions with that prefix exist! Try using `/faq list` to see available prefixes.")
        else:
            await intr.response.send_message(embed=embed)
    
    # faq new <question> <answer> <prefix> [category]
    @app_commands.command(
        name="new", description="add a new question to the faq sheet"
    )
    @app_commands.describe(question="Question to add")
    @app_commands.describe(answer="Answer to add")
    @app_commands.describe(prefix="Prefix to add")
    @app_commands.describe(category="Category to add")
    async def new(self, intr: discord.Interaction, question: str, answer: str, prefix: str, category: str = None):
        if not self.isAdmin(intr.user):
            await intr.response.send_message("You do not have permission to modify the faq sheet!")
            return
        
        if category == None:
            category = "General"

        # dont add question if the prefix already exists
        data = self.faq_sheet.get_all_records()
        df = pd.DataFrame(data)
        for index, row in df.iterrows():
            if row['Prefix'] == prefix:
                await intr.response.send_message("Prefix already exists!")
                return

        self.faq_sheet.append_row([question, answer, 1, category, prefix])
        await intr.response.send_message("Added new question to faq sheet!")

    # faq delete <prefix>
    @app_commands.command(
        name="delete", description="delete a question from the faq sheet"
    )
    @app_commands.describe(prefix="Prefix to delete")
    async def delete(self, intr: discord.Interaction, prefix: str):
        if not self.isAdmin(intr.user):
            await intr.response.send_message("You do not have permission to modify the faq sheet!")
            return

        data = self.faq_sheet.get_all_records()
        df = pd.DataFrame(data)

        # delete the row with the prefix
        for index, row in df.iterrows():
            if row['Prefix'] == prefix:
                self.faq_sheet.delete_row(index + 2)
                await intr.response.send_message("Deleted question from faq sheet!")
                return

        await intr.response.send_message("Prefix not found!")
    
    # faq edit <prefix> <question> <answer> <category>
    @app_commands.command(
        name="edit", description="edit a question from the faq sheet"
    )
    @app_commands.describe(prefix="Prefix to edit")
    @app_commands.describe(question="Question to edit")
    @app_commands.describe(answer="Answer to edit")
    @app_commands.describe(category="Category to edit")
    async def edit(self, intr: discord.Interaction, prefix: str, question: str = None, answer: str = None, category: str = None):
        if not self.isAdmin(intr.user):
            await intr.response.send_message("You do not have permission to modify the faq sheet!")
            return

        data = self.faq_sheet.get_all_records()
        df = pd.DataFrame(data)

        # edit the row with the prefix
        for index, row in df.iterrows():
            if row['Prefix'] == prefix:
                if question != None:
                    self.faq_sheet.update_cell(index + 2, 1, question)
                if answer != None:
                    self.faq_sheet.update_cell(index + 2, 2, answer)
                if category != None:
                    self.faq_sheet.update_cell(index + 2, 4, category)
                await intr.response.send_message("Edited question from faq sheet!")
                return
            
        await intr.response.send_message("Prefix not found!")

async def setup_faq(bot, guilds):
    cog = Faq()
    await cog.load_sheet()
    await bot.add_cog(cog, guilds=guilds)
