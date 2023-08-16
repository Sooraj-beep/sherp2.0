from typing import List, Optional
import discord
from discord.ext import commands

STARBOARD_CHANNEL_ID = 1133260871049691257  # 1139734225390669875
ON_PHONE_EMOJI_STR = "<:OnPhone:1062142401973588039>"  # "<:OnP:1139749947357544500>"


class Starboard(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.starboard_emoji_str = ON_PHONE_EMOJI_STR
        self.threshold = 3
        # Starboarded Message ID -> ID of the message the bot sent.
        self.starboard_msgs = dict()
        self.starboard_channel = bot.get_channel(STARBOARD_CHANNEL_ID)

    async def cog_load(self):
        await super().cog_load()
        print("Starboard Cog loaded.")

    def _get_title(self, react: discord.Reaction) -> str:
        return f"{self.starboard_emoji_str} x **{react.count}** |{react.message.channel.mention}"

    async def _get_open_msg_view(self, msg: discord.Message) -> discord.ui.View:
        btn = discord.ui.Button(label="Jump", url=msg.jump_url)
        v = discord.ui.View().add_item(btn)

        if msg.type != discord.MessageType.reply:
            return v

        reply = msg.reference.cached_message or await msg.channel.fetch_message(
            msg.reference.message_id
        )
        return v.add_item(discord.ui.Button(label="Context", url=reply.jump_url))

    async def update_reaction_count(self, react: discord.Reaction) -> None:
        msg_id = self.starboard_msgs[react.message.id]
        msg: discord.Message = await self.starboard_channel.fetch_message(msg_id)
        await msg.edit(content=self._get_title(react))

    def _get_first_viable_attachment_url(self, atmnts: List[discord.Attachment]) -> str:
        for a in atmnts:
            if a.url.endswith(("png", "jpeg", "jpg", "gif", "webp")):
                return a.url

    def _get_starboard_embed(self, msg: discord.Message) -> discord.Embed:
        embed = discord.Embed(
            description=msg.content or msg.system_content,
            color=discord.Color.dark_green(),
        ).set_author(name=msg.author.display_name, icon_url=msg.author.avatar.url)

        if u := self._get_first_viable_attachment_url(msg.attachments):
            embed.set_image(url=u)

        return embed

    async def _build_embeds(self, msg: discord.Message) -> List[discord.Embed]:
        main_embed = self._get_starboard_embed(msg)

        if msg.type != discord.MessageType.reply:
            return [main_embed]

        reply_to = msg.reference.cached_message or await msg.channel.fetch_message(
            msg.reference.message_id
        )
        atcmnt_url = self._get_first_viable_attachment_url(reply_to.attachments)
        # If the replied to message has no attachments, we simply add a field
        # to the main embed.
        if not atcmnt_url:
            main_embed.add_field(
                name="Reply to the message:",
                value=reply_to.content or reply_to.system_content,
            )
            return [main_embed]

        # If the replied-to message has attachments, we need another embed.
        reply_embed = discord.Embed(
            title="Reply to this message:",
            description=reply_to.content or reply_to.system_content,
            color=discord.Color.dark_green(),
        ).set_image(url=atcmnt_url)

        return [main_embed, reply_embed]

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
