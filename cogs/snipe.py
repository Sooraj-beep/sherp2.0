import discord
from discord.ext import commands
from datetime import datetime, timedelta

import aiohttp, os

class DeletedMsg:
    def __init__(self, msg, attachment_path=None):
        self.msg = msg
        self.attachment_path = attachment_path
        self.time = datetime.utcnow()

SNIPE_TIMER = 10
class Snipe(commands.Cog):
    def __init__(self):
        self.deleted_messages = {}

    async def cog_load(self):
        await super().cog_load()
        print("Snipe Cog loaded.")

    async def save_attachment(self, attachment):
        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as resp:
                if resp.status != 200:
                    return -1
                filename = os.path.join('attachments', attachment.filename) # save to ./attachments
                with open(filename, 'wb') as f:
                    f.write(await resp.read())
                return filename

    @commands.command(name="snipe")
    async def snipe(self, ctx):
        curr_time = datetime.utcnow()
        msg = self.deleted_messages.pop(ctx.channel.id, None)
        if not msg or curr_time - msg.time > timedelta(seconds=SNIPE_TIMER):
            await ctx.send(f"Nothing found")
            return
        embed = discord.Embed(description=f"**{msg.msg.author.name}** said: {msg.msg.content}", color=0x00ff00)
        if msg.attachment_path:
            file = discord.File(msg.attachment_path, filename=msg.attachment_path.split("/")[-1])
            embed.set_image(url=f"attachment://{file.filename}")
            await ctx.send(embed=embed, file=file)
        else:
            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        attachment_path = None
        if message.attachments:
            attachment_path = await self.save_attachment(message.attachments[0])
        self.deleted_messages[message.channel.id] = DeletedMsg(message, attachment_path)

async def setup_snipe(bot, guilds):
    cog = Snipe()
    await bot.add_cog(cog, guilds=guilds)
