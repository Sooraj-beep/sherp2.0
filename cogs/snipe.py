import discord
from discord import Embed, File, Attachment, Message
from discord.ext import commands
from collections import defaultdict

import asyncio
from io import BytesIO
from helper import get_config

from typing import List, Tuple

__cfg = get_config().get("snipe", None)
SNIPE_TIMER = __cfg.get("timer", 10) if __cfg else 10


class DeletedMsg:
    def __init__(self, msg: Message, attachments: List[Tuple[str, BytesIO]]):
        self.msg = msg
        self.attachments = attachments


class Snipe(commands.Cog):
    def __init__(self, bot, http_client):
        self.__bot = bot
        self.http = http_client
        self.deleted_messages = defaultdict(lambda: set())
        self.__lock = asyncio.Lock()

    async def cog_load(self):
        await super().cog_load()
        print("Snipe Cog loaded.")

    async def save_attachment(self, attachment: Attachment):
        async with self.http.get(attachment.url) as resp:
            if resp.status != 200:
                return attachment.filename, None
            buf = BytesIO()
            buf.write(await resp.read())
            buf.seek(0)
            return attachment.filename, buf

    @commands.command(name="snipe")
    async def snipe(self, ctx):
        msgs = None
        async with self.__lock:
            msgs = self.deleted_messages[ctx.channel.id].copy()

        if not msgs:
            await ctx.send("Nothing found!")
            return

        sniped = []
        for deleted_msg in msgs:
            msg = deleted_msg.msg
            author_name = f"{msg.author.display_name}({msg.author.name})"
            heading = Embed(description=msg.content, color=0x00FF00).set_author(
                name=author_name, icon_url=msg.author.avatar.url
            )
            embeds = [heading]
            files = [File(buf, filename=fname) for fname, buf in msg.attachments if buf]
            attachment_embeds = [
                Embed().set_image(url=f"attachment://{f.filename}") for f in files
            ]
            embeds.extend(attachment_embeds)
            await ctx.send(embeds=embeds, files=files)
            sniped.append(deleted_msg)

        async with self.__lock:
            msgs = self.deleted_messages[ctx.channel.id]
            for msg in sniped:
                msgs.discard(msg)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        attachments = []
        if message.attachments:
            attachments = await asyncio.gather(
                *[self.save_attachment(a) for a in message.attachments]
            )
        deleted_msg = DeletedMsg(message, attachments)
        async with self.__lock:
            self.deleted_messages[message.channel.id].add(deleted_msg)
        await asyncio.sleep(SNIPE_TIMER)
        async with self.__lock:
            self.deleted_messages[message.channel.id].discard(deleted_msg)


async def setup_snipe(bot, guilds, client):
    cog = Snipe(bot, client)
    await bot.add_cog(cog, guilds=guilds)
