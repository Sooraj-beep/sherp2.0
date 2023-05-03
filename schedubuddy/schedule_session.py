from schedubuddy.draw_sched import draw_schedule

import json, requests
from io import BytesIO
from contextlib import suppress
import asyncio
import discord
from discord import Colour, Embed, HTTPException, Message, Reaction, User
from discord.ext import commands
from discord.ext.commands import CheckFailure, Cog as DiscordCog, Command, Context

SCHEDUBUDDY_ROOT = 'https://schedubuddy1.herokuapp.com//api/v1/'
LEFT_EMOJI = '⬅️'
RIGHT_EMOJI = '➡️'

class ScheduleSession:
    def __init__(
        self,
        ctx: Context,
        *args,
    ):
        self._ctx = ctx
        self._bot = ctx.bot
        self.title = "Schedule Session"
        self.author = ctx.author
        self.destination = ctx.channel
        self.message = None
        self._pages = None
        self._current_page = 0
        self._timeout_task = None
        self.schedules = self.get_schedules(args)
        self.aliases = self.schedules['objects']['aliases']
        self.reset_timeout()

    @staticmethod
    def get_schedules(args):
        termid = None
        term = args[0]
        year = args[1]
        if term.lower() in ['f', 'fa', 'fall']: term = 'Fall'
        elif term.lower() in ['w', 'wi', 'win', 'wint', 'winter']: term = 'Winter'
        elif term.lower() in ['sp', 'spr', 'spring']: term = 'Spring'
        elif term.lower() in ['su', 'sum', 'summ', 'summer']: term = 'Summer'
        if year in ['2023', '23']: year = '2023'
        elif year in ['2024', '24']: year = '2024'
        termid = None
        if year == '2023':
            if term == 'Winter': termid = '1820'
            elif term == 'Spring': termid = '1830'
            elif term == 'Summer': termid = '1840'
            elif term == 'Fall': termid = '1850'
        elif year == '2024':
            if term == 'Winter': termid = '1860'
        # gen-schedules/?term=1850&courses=[STAT%20151,STAT%20235]&evening=1&online=1&start=10:00%20AM&consec=2&limit=30
        tokens = args[2:]
        evening_pref = '1'
        start_pref = '10:00%20AM'
        consec_pref = '2'
        courses_str_list = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.startswith("--"):
                option, val = token.split("=")
                option = option[2:].lower()
                if option == "evening":
                    if val.lower() == "false" or val == '0':
                        evening_pref = '0'
                if option == 'start':
                    colon = val.index(':')
                    hrs = val[:colon]
                    mins = val[colon+1 : colon+3]
                    ampm = val[colon+3 : colon+5]
                    start_pref = f'{hrs}:{mins}%20{ampm}'
                if option == 'consec':
                    consec_pref = val
            else:
                # consume tokens until a token with a number appears
                course_name = ''
                token_has_num = False
                while not token_has_num and i < len(tokens) + 1:
                    token = tokens[i] 
                    course_name += token.upper() 
                    for char in token:
                        if char.isdigit():
                            token_has_num = True
                    if not token_has_num:
                        course_name += '%20'
                    i += 1
                courses_str_list.append(course_name)
                i -= 1
            i += 1
        courses_str = '[' + ','.join(courses_str_list) + ']'
        url = SCHEDUBUDDY_ROOT + f'gen-schedules/?term={termid}&courses={courses_str}&evening={evening_pref}&online=1&start={start_pref}&consec={consec_pref}&limit=30'
        print(url)
        response = requests.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)
            return data

    async def update_page(self, page_number: int = 0) -> None:
        self._current_page = page_number
        embed = Embed(description=f'Listing **{self._current_page+1}**\
            of **{len(self._pages)}** pages', color=0xb3edbd)
        embed.set_author(name=self.author.display_name,
                        icon_url=self.author.avatar_url)
        footer_msg = ""
        if len(self.aliases) > 0:
            footer_msg = "View class aliases at schedubuddy.com"
        if len(footer_msg) > 0:
            embed.set_footer(text=footer_msg)
        image = draw_schedule(self.schedules['objects']['schedules'][page_number])
        bufferedio = BytesIO()
        image.save(bufferedio, format="PNG")
        bufferedio.seek(0)
        file = discord.File(bufferedio, filename="image.png")
        embed.set_image(url="attachment://image.png")
        self.new_message = await self.destination.send(file=file, embed=embed)
        if self.message:
            await self.message.delete()
        self.message = self.new_message
        self._bot.loop.create_task(self.message.add_reaction(LEFT_EMOJI))
        self._bot.loop.create_task(self.message.add_reaction(RIGHT_EMOJI))

    async def build_pages(self) -> None:
        self._pages = self.schedules['objects']['schedules']

    async def prepare(self) -> None:
        await self.build_pages()
        await self.update_page()
        self._bot.add_listener(self.on_reaction_add)

    @classmethod
    async def start(cls, ctx: Context, *command, **options) -> "ScheduleSession":
        session = cls(ctx, *command, **options)
        await session.prepare()
        return session

    async def stop(self) -> None:
        self._bot.remove_listener(self.on_reaction_add)
        await self.message.clear_reactions()

    async def timeout(self, seconds: int = 180) -> None:
        await asyncio.sleep(seconds)
        await self.stop()

    def reset_timeout(self) -> None:
        if self._timeout_task:
            if not self._timeout_task.cancelled():
                self._timeout_task.cancel()
        self._timeout_task = self._bot.loop.create_task(self.timeout())

    async def do_back(self) -> None:
        if self._current_page != 0:
            await self.update_page(self._current_page-1)
        else:
            await self.update_page(len(self._pages)-1)

    async def do_next(self) -> None:
        if self._current_page != (len(self._pages)-1):
            await self.update_page(self._current_page+1)
        else:
            await self.update_page(0)

    async def on_reaction_add(self, reaction: Reaction, user: User) -> None:
        emoji = str(reaction.emoji)
        if (reaction.message.id != self.message.id) or\
           (user.id != self.author.id) or\
           (emoji not in (LEFT_EMOJI, RIGHT_EMOJI)):
            return
        self.reset_timeout()
        if emoji == LEFT_EMOJI:
            await self.do_back()
        elif emoji == RIGHT_EMOJI:
            await self.do_next()
        with suppress(HTTPException):
            await self.message.remove_reaction(reaction, user)

class Schedule(commands.Cog):
    @commands.command('sched')
    async def new_schedule(self, ctx: Context, *args) -> None:
        try:
            await ScheduleSession.start(ctx, *args)
        except commands.errors.CommandError as e:
            embed = Embed()
            embed.colour = Colour.red()
            embed.title = str(e)
            await ctx.send(embed=embed)

def setup(bot: commands.Bot) -> None:
    bot.add_cog(Schedule())
