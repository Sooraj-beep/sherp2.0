from typing import List, Optional
import discord
from discord.ext import commands
from discord import ui

STARBOARD_CHANNEL_ID = 1133260871049691257  # 1139734225390669875
ON_PHONE_EMOJI_STR = "<:OnPhone:1062142401973588039>"  # "<:OnP:1139749947357544500>"


class Starboard(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.starboard_emoji_str = ON_PHONE_EMOJI_STR
        self.threshold = 1
        # Starboarded Message ID -> ID of the message the bot sent.
        self.starboard_msgs = dict()
        self.starboard_channel = bot.get_channel(STARBOARD_CHANNEL_ID)

    async def cog_load(self):
        await super().cog_load()
        print("Starboard Cog loaded.")

    def _get_title(self, react: discord.Reaction) -> str:
        return f"{self.starboard_emoji_str} x **{react.count}** |{react.message.channel.mention}"

    async def _get_open_msg_view(self, msg: discord.Message) -> ui.View:
        btn = ui.Button(label="Jump", url=msg.jump_url)
        v = ui.View().add_item(btn)
        if msg.type == discord.MessageType.reply:
            reply = msg.reference.cached_message
            if not reply:
                reply = await msg.channel.fetch_message(msg.reference.message_id)
            v.add_item(ui.Button(label="Context", url=reply.jump_url))
        return v

    async def update_reaction_count(self, react: discord.Reaction) -> None:
        msg_id = self.starboard_msgs[react.message.id]
        msg: discord.Message = await self.starboard_channel.fetch_message(msg_id)
        # No way to get the view from the old message
        old_view = await self._get_open_msg_view(react.message)
        await msg.edit(content=self._get_title(react), embeds=msg.embeds)

    def _get_starboard_embed(
        self, msg: discord.Message, add_author: bool = True
    ) -> discord.Embed:
        embed = discord.Embed(
            description=msg.content or msg.system_content,
            color=discord.Color.dark_green(),
        )

        for a in msg.attachments:
            if a.url.endswith(("png", "jpeg", "jpg", "gif", "webp")):
                embed.set_image(url=a.url)
                break  # only one image embedded for now.

        if add_author:
            return embed.set_author(
                name=msg.author.display_name, icon_url=msg.author.avatar.url
            )
        else:
            return embed

    async def _build_embeds(self, msg: discord.Message) -> List[discord.Embed]:
        if msg.type == discord.MessageType.reply:
            reply_to = msg.reference.cached_message
            if not reply_to:
                reply_to = await msg.channel.fetch_message(msg.reference.message_id)
            embed = self._get_starboard_embed(msg)
            reply_embed = self._get_starboard_embed(reply_to, False)
            reply_embed.title = "Reply to this message:"
            return [embed, reply_embed]
        return [self._get_starboard_embed(msg)]

    async def create_starboard_post(self, react: discord.Reaction):
        embeds = await self._build_embeds(react.message)
        open_msg_view = await self._get_open_msg_view(react.message)
        msg: discord.Message = await self.starboard_channel.send(
            self._get_title(react), embeds=embeds, view=open_msg_view
        )
        self.starboard_msgs[react.message.id] = msg.id

    @commands.Cog.listener()
    async def on_reaction_add(self, react: discord.Reaction, _: discord.User):
        if str(react.emoji) != self.starboard_emoji_str:
            return

        if react.message.channel.is_nsfw():
            return

        if react.count < self.threshold:
            return

        if react.message.id in self.starboard_msgs:
            await self.update_reaction_count(react)
        else:
            await self.create_starboard_post(react)

    @commands.Cog.listener()
    async def on_reaction_remove(self, react: discord.Reaction, _: discord.User):
        if str(react.emoji) != self.starboard_emoji_str:
            return

        if not react.message.id in self.starboard_msgs:
            return

        await self.update_reaction_count(react)

    @commands.Cog.listener()
    async def on_message_delete(self, msg: discord.Message):
        if msg_id := self.starboard_msgs.get(msg.id, None):
            m = await self.starboard_channel.fetch_message(msg_id)
            await m.delete()


async def setup_starboard(bot, guilds):
    await bot.add_cog(Starboard(bot), guilds=guilds)
