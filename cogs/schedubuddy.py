import asyncio
import json
from io import BytesIO
from typing import Optional
from urllib.parse import quote

import discord
from aiohttp import ClientSession
from discord import Embed, app_commands
from discord.ext import commands

from cogs.helpers.draw_schedule import draw_schedule

SCHEDUBUDDY_ROOT = "https://schedubuddy1.herokuapp.com/api/v1/"
LEFT_EMOJI = "⬅️"
RIGHT_EMOJI = "➡️"


class ScheduleSession:
    def __init__(
        self,
        bot,
        term_id: str,
        start_pref: str,
        consec_pref: str,
        evening_pref: str,
        http_client: ClientSession,
        *courses,
    ):
        self.__bot = bot
        self.term_id = term_id
        self.start_pref = start_pref
        self.consec_pref = consec_pref
        self.evening_pref = evening_pref
        self.http = http_client
        self.courses = courses
        self.intr = None
        self.__timer = None
        self.raw_schedules = None
        self.pages = []
        self.aliases = []
        self.current_page = 0
        self.response_embed = None
        self.author = None

    async def start(self, intr: discord.Interaction):
        self.author = intr.user
        should_cont = await self.fetch_schedules(intr)
        if not should_cont:
            return
        should_cont = await self.send_response(intr)
        if not should_cont:
            return
        self.__bot.add_listener(self.on_reaction_add)
        self.reset_timer()
        await intr.response.send_message("Created schedule.")

    async def fetch_schedules(self, intr: discord.Interaction):
        courses = (
            "["
            + ",".join(map(lambda s: s.upper(), filter(lambda s: s, self.courses)))
            + "]"
        )
        print(courses)
        url = SCHEDUBUDDY_ROOT + "gen-schedules/"
        params = {
            "term": self.term_id,
            "courses": courses,
            "evening": self.evening_pref,
            "online": 1,
            "start": self.start_pref,
            "consec": self.consec_pref,
            "limit": 30,
            "blacklist": "[]",
        }
        async with self.http.get(url, params=params) as resp:
            print(str(resp.url))
            if resp.status != 200:
                await intr.response.send_message(
                    "Schedule buddy returned non 200 response"
                )
                return False
            self.raw_schedules = json.loads(await resp.text())
            self.pages = self.raw_schedules["objects"]["schedules"]
            self.aliases = self.raw_schedules["objects"]["aliases"]
            return True

    async def timeout(self, seconds=60):
        await asyncio.sleep(seconds)
        await self.stop()

    async def stop(self):
        self.__bot.remove_listener(self.on_reaction_add)
        await self.response_embed.clear_reactions()
        print("Stopped Schedule Session")

    def reset_timer(self):
        if self.__timer:
            if not self.__timer.cancelled():
                self.__timer.cancel()
        self.__timer = self.__bot.loop.create_task(self.timeout())

    def build_embed(self, display_name, schedule) -> Embed:
        embed = Embed(
            description=f"Listing **{self.current_page+1}**\
            of **{len(self.pages)}** pages",
            color=0xB3EDBD,
        )
        embed.set_author(name=display_name)
        if self.aliases:
            embed.set_footer(text="View class aliases at schedubuddy.com")

        image = draw_schedule(schedule)
        bufferedio = BytesIO()
        image.save(bufferedio, format="PNG")
        bufferedio.seek(0)
        file = discord.File(bufferedio, filename="image.png")
        embed.set_image(url="attachment://image.png")
        return embed, file

    async def send_response(self, intr: discord.Interaction):
        if not self.pages:
            await intr.response.send_message("No schedule found!")
            return False
        embed, file = self.build_embed(intr.user.display_name, self.pages[0])
        channel = self.__bot.get_channel(intr.channel_id)
        self.response_embed = await channel.send(embed=embed, file=file)
        await self.response_embed.add_reaction(LEFT_EMOJI)
        await self.response_embed.add_reaction(RIGHT_EMOJI)
        return True

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if (reaction.message.id != self.response_embed.id) or (
            user.id != self.author.id
        ):
            return

        emoji = str(reaction.emoji)
        if emoji != LEFT_EMOJI and emoji != RIGHT_EMOJI:
            return

        if emoji == LEFT_EMOJI:
            self.current_page -= 1
        else:
            self.current_page += 1

        self.reset_timer()
        self.current_page = self.current_page % len(self.pages)
        embed, file = self.build_embed(user.display_name, self.pages[self.current_page])
        await self.response_embed.edit(embed=embed, attachments=[file])
        await self.response_embed.remove_reaction(reaction, user)
        print("Tried to update the schedule embed")


class Schedubuddy(commands.GroupCog, name="schedubuddy"):
    def __init__(self, bot, http_client):
        self.http = http_client
        self.__bot = bot

    async def cog_load(self):
        await super().cog_load()
        print("ScheduleBuddy Cog loaded.")

    def get_term_id(self, year: str, term: str):
        match (year.value, term.value):
            case ("2023", "Winter"):
                return "1820"
            case ("2023", "Spring"):
                return "1830"
            case ("2024", "Summer"):
                return "1840"
            case ("2023", "Fall"):
                return "1850"
            case ("2024", "Winter"):
                return "1860"
            case _:
                return ""

    @app_commands.command(
        name="view-schedule",
        description="View the courses scheduled in a given hall/room.",
    )
    @app_commands.describe(term="The term to view.")
    @app_commands.choices(
        term=[
            app_commands.Choice(name="Fall", value="Fall"),
            app_commands.Choice(name="Winter", value="Winter"),
            app_commands.Choice(name="Spring", value="Spring"),
            app_commands.Choice(name="Summer", value="Summer"),
        ]
    )
    @app_commands.describe(year="The year to view the schedule for.")
    @app_commands.choices(
        year=[
            app_commands.Choice(name="2023", value="2023"),
            app_commands.Choice(name="2024", value="2024"),
        ]
    )
    @app_commands.describe(room="The room to view the schedule for. Eg CAB 239")
    async def view(
        self,
        intr: discord.Interaction,
        term: app_commands.Choice[str],
        year: app_commands.Choice[str],
        room: str,
    ):
        term_id = self.get_term_id(year, term)
        if term_id == "":
            await intr.response.send_message("Invalid arguments chosen for year/term.")
            return

        url = SCHEDUBUDDY_ROOT + "room-sched/"
        params = {"term": term_id, "room": room.upper()}
        async with self.http.get(url, params=params) as resp:
            if resp.status != 200:
                await intr.response.send_message(
                    "Error fetching data from schedulebuddy"
                )
                return
            data = json.loads(await resp.text())
            image = draw_schedule(data["objects"]["schedules"][0])
            bufferedio = BytesIO()
            image.save(bufferedio, format="PNG")
            bufferedio.seek(0)
            file = discord.File(bufferedio, filename="image.png")
            await intr.response.send_message(file=file)

    @app_commands.command(
        name="create-schedule",
        description="Given a set of courses, create legal schedules.",
    )
    @app_commands.describe(term="The term to view.")
    @app_commands.choices(
        term=[
            app_commands.Choice(name="Fall", value="Fall"),
            app_commands.Choice(name="Winter", value="Winter"),
            app_commands.Choice(name="Spring", value="Spring"),
            app_commands.Choice(name="Summer", value="Summer"),
        ]
    )
    @app_commands.describe(year="The year to view the schedule for.")
    @app_commands.choices(
        year=[
            app_commands.Choice(name="2023", value="2023"),
            app_commands.Choice(name="2024", value="2024"),
        ]
    )
    @app_commands.describe(
        course1='Course code of the course you want to schedule. Eg "CMPUT 174". The space is important.'
    )
    @app_commands.choices()
    @app_commands.choices()
    async def create_schedule(
        self,
        intr: discord.Interaction,
        year: app_commands.Choice[str],
        term: app_commands.Choice[str],
        course1: str,
        course2: Optional[str] = "",
        course3: Optional[str] = "",
        course4: Optional[str] = "",
        course5: Optional[str] = "",
        course6: Optional[str] = "",
        course7: Optional[str] = "",
        start_time: Optional[str] = "10:00 AM",
        evening_pref: Optional[str] = "1",
        consec_pref: Optional[str] = "1",
    ):
        term_id = self.get_term_id(year, term)
        session = ScheduleSession(
            self.__bot,
            term_id,
            start_time,
            consec_pref,
            evening_pref,
            self.http,
            course1,
            course2,
            course3,
            course4,
            course5,
            course6,
            course7,
        )
        await session.start(intr)


async def setup_schedule_buddy(bot, guilds, client):
    cog = Schedubuddy(bot, client)
    await bot.add_cog(cog, guilds=guilds)
