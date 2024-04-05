import discord
from discord.ext import commands
from discord import app_commands

# I couldn't work out replying directly to the initial messages so this is not the best
# Nonetheless it is nearly 6am and I felt the need to complete this
# I hope it works out and nobody abuses it lol good luck

class sherpMailbox(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sherp = ""
    
    async def cog_load(self):
        await super().cog_load()
        print("Sherpmail loaded.")

    @app_commands.command(
        name = "sherpmail",
        description = "Leave a message directly to Sherp's DMs"
    )
    @app_commands.describe(
        msg = "The message you would like to leave for Sherp (be respectful)"
    )
    async def sendMessage(self, interaction: discord.Interaction, msg: str):
        # Sherp's Discord ID is currently 212613981465083906
        self.sherp = await interaction.client.fetch_user(212613981465083906)
        try:
            embed = discord.Embed(
                title = f"📬 You've got mail! **@{interaction.user} | ID: {interaction.user.id}** sent you the following:",
                description = f"{msg}",
                colour = discord.Colour.gold()
            )
            await self.sherp.send(embed = embed)
            
            embed = discord.Embed(
                title = f"📫 Outgoing! The following message has been mailed to {self.sherp.display_name}:",
                description = f"{msg}",
                colour = discord.Colour.green()
            )
            await interaction.response.send_message(embed = embed)
        except:
            await interaction.response.send_message(f"❌ An unexpected error has occurred!")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if (message.guild == None) and (message.author.id == 214657501193306112):
            try:
                embed = discord.Embed(
                    title = "📬 You've got mail! This is what Sherp said:",
                    description = f"{message.content}",
                    colour = discord.Colour.gold()
                )
                # I used the ID 1183281507842924645 from the channel "non-cs-nonsense"
                ch = self.bot.get_channel(1183281507842924645)
                await ch.send(embed = embed)

                embed = discord.Embed(
                    title = f"📫 Outgoing! The following reply was sent:",
                    description = f"{message.content}",
                    colour = discord.Colour.green()
                )
                await message.reply(embed = embed, mention_author = False)
            except:
                await message.reply(f"❌ An unexpected error has occurred!")

async def setup_sherpMailbox_cog(bot, guilds):
    await bot.add_cog(sherpMailbox(bot), guilds=guilds)