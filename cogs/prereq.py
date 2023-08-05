import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice

import json

class PreReq(commands.Cog, name="prereq"):
    def __init__(self):
        self.catalog = {}

    async def cog_load(self):
        await super().cog_load()
        print("PreReq Cog Loaded")

    async def load_data(self):
        with open("data/ualberta.ca.json", "r", encoding='utf-8') as f:
            self.catalog = json.load(f)

    @app_commands.command(name="prereq", description="Get prerequisites for a given course.")
    @app_commands.describe(department="The department code like CMPUT or MATH")
    @app_commands.describe(course="The course code like 229 or 225 for CMPUT 229 or MATH 225")
    async def prereq(self, intr: discord.Interaction, department: str, course: str):
        dept, course = department.strip().upper(), course.strip().upper()
        if not dept in self.catalog['courses']:
            await intr.response.send_message(f'Could not find **{dept}**')
            return
        if not course in self.catalog['courses'][dept]:
            await intr.response.send_message(f'Could not find **{course}** in the {dept} department')
            return
        catalog_obj = self.catalog['courses'][dept][course]
        course_name = catalog_obj['name']
        prereqs = catalog_obj.get('raw', 'No prerequisites')
        await intr.response.send_message(f'**{dept} {course} - {course_name}**\n{prereqs}')

async def setup_prereq(bot, guilds):
    cog = PreReq()
    await cog.load_data()
    await bot.add_cog(cog, guilds=guilds)





