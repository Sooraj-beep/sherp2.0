import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice

import json
from typing import Optional


class CourseInfo(commands.GroupCog, name="course"):
    def __init__(self):
        self.catalog = {}

    async def cog_load(self):
        await super().cog_load()
        print("PreReq Cog Loaded")

    async def load_data(self):
        with open("data/ualberta.ca.json", "r", encoding="utf-8") as f:
            self.catalog = json.load(f)
            self.courses = self.catalog["courses"]

    async def get_course_or_err(
        self, dept: str, course: str, intr: discord.Interaction
    ) -> Optional[dict]:
        if not dept in self.courses:
            await intr.response.send_message(f"Could not find **{dept}**")
            return None

        if not course in self.courses[dept]:
            await intr.response.send_message(
                f"Could not find **{course}** in the {dept} department"
            )
            return None
        return self.courses[dept][course]

    @app_commands.command(
        name="prereq", description="Get prerequisites for a given course."
    )
    @app_commands.describe(department="The department code like CMPUT or MATH")
    @app_commands.describe(
        course="The course code like 229 or 225 for CMPUT 229 or MATH 225"
    )
    async def prerequisites(
        self, intr: discord.Interaction, department: str, course: str
    ):
        dept, course = department.strip().upper(), course.strip().upper()
        course_info = await self.get_course_or_err(dept, course, intr)
        if not course_info:
            return
        course_name = course_info["name"]
        prereqs = course_info.get("raw", "No prerequisites")
        await intr.response.send_message(
            f"**{dept} {course} - {course_name}**\n{prereqs}"
        )

    @app_commands.command(
        name="desc", description="Get the description for a given course."
    )
    @app_commands.describe(department="The department code like CMPUT or MATH")
    @app_commands.describe(
        course="The course code like 229 or 225 for CMPUT 229 or MATH 225"
    )
    async def description(
        self, intr: discord.Interaction, department: str, course: str
    ):
        dept, course = department.strip().upper(), course.strip().upper()
        course_info = await self.get_course_or_err(dept, course, intr)
        if not course_info:
            return
        if not "desc" in course_info:
            await intr.response.send_message(
                f"There is no available course description for **{dept} {course}**."
            )
            return

        course_name = course_info["name"]
        course_faculty = course_info["faculty"]
        course_desc = course_info["desc"]
        await intr.response.send_message(
            f"**{dept} {course} - {course_name}**\n{course_faculty}\n{course_desc}"
        )


async def setup_course_info(bot, guilds):
    cog = CourseInfo()
    await cog.load_data()
    await bot.add_cog(cog, guilds=guilds)
