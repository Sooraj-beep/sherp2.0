import discord
from discord.ext import commands
from discord import app_commands
from typing import Dict, List, Tuple, Optional
import asyncio
from datetime import datetime, timedelta, timezone


class LeaderboardView(discord.ui.View):
    """View for paginated leaderboard display"""

    def __init__(self, entries: List[Tuple[str, int]], per_page: int = 10):
        super().__init__(timeout=60)
        self.entries = entries
        self.per_page = per_page
        self.current_page = 0
        self.max_page = (len(entries) - 1) // per_page

    def get_embed(self) -> discord.Embed:
        """Generate the embed for the current page"""
        start = self.current_page * self.per_page
        end = min(start + self.per_page, len(self.entries))

        embed = discord.Embed(
            title="📊 Message Leaderboard",
            description=f"Showing users {start + 1}-{end} of {len(self.entries)}",
            color=discord.Color.gold(),
        )

        leaderboard_text = []
        for i, (user_id, count) in enumerate(self.entries[start:end], start=start + 1):
            # Get medal emoji for top 3
            medal = ""
            if i == 1:
                medal = "🥇 "
            elif i == 2:
                medal = "🥈 "
            elif i == 3:
                medal = "🥉 "

            leaderboard_text.append(f"{medal}**{i}.** <@{user_id}> - **{count:,}** messages")

        embed.add_field(
            name="Rankings",
            value=("\n".join(leaderboard_text) if leaderboard_text else "No data available"),
            inline=False,
        )

        embed.set_footer(text=f"Page {self.current_page + 1}/{self.max_page + 1}")
        return embed

    def update_buttons(self):
        """Update button states based on current page"""
        self.first_page.disabled = self.current_page == 0
        self.prev_page.disabled = self.current_page == 0
        self.next_page.disabled = self.current_page == self.max_page
        self.last_page.disabled = self.current_page == self.max_page

    @discord.ui.button(label="<<", style=discord.ButtonStyle.secondary)
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 0
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="<", style=discord.ButtonStyle.primary)
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = max(0, self.current_page - 1)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label=">", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = min(self.max_page, self.current_page + 1)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label=">>", style=discord.ButtonStyle.secondary)
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = self.max_page
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    async def on_timeout(self):
        """Disable all buttons when the view times out"""
        for item in self.children:
            item.disabled = True


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        """Load when cog loads"""
        await super().cog_load()
        print("Leaderboard Cog loaded.")

    async def count_channel_messages(self, channel, user, after_date=None, completed_callback=None) -> int:
        """Count messages for a user in a single channel"""
        try:
            channel_count = 0
            # Use after parameter if provided for faster processing
            history_kwargs = {"limit": None}
            if after_date:
                history_kwargs["after"] = after_date

            async for message in channel.history(**history_kwargs):
                if message.author.id == user.id and not message.author.bot:
                    channel_count += 1

            if channel_count > 0:
                print(f"Channel {channel.name}: {channel_count} messages")

            # Call completed callback if provided - do this BEFORE returning
            if completed_callback:
                try:
                    await completed_callback()
                except Exception as e:
                    print(f"Error in channel completion callback: {e}")

            return channel_count

        except discord.Forbidden:
            print(f"No access to channel: {channel.name}")
            if completed_callback:
                try:
                    await completed_callback()
                except Exception as e:
                    print(f"Error in channel completion callback: {e}")
            return 0
        except discord.HTTPException as e:
            print(f"HTTP error in {channel.name}: {str(e)}")
            if completed_callback:
                try:
                    await completed_callback()
                except Exception as e:
                    print(f"Error in channel completion callback: {e}")
            return 0

    async def get_user_message_count(
        self,
        guild: discord.Guild,
        user: discord.Member,
        progress_callback=None,
        after_date=None,
        channel_completed_callback=None,
    ) -> int:
        """Get total message count for a user in a guild using filtered history"""
        # Get all channels that can contain messages
        channels = [channel for channel in guild.channels if isinstance(channel, (discord.TextChannel, discord.Thread))]

        # Get forum channels separately to handle their threads
        forum_channels = [channel for channel in guild.channels if isinstance(channel, discord.ForumChannel)]

        # Count accessible channels first (only check bot permissions)
        accessible_channels = []
        for channel in channels:
            if channel.permissions_for(guild.me).read_messages:
                accessible_channels.append(channel)

        accessible_forums = []
        for forum in forum_channels:
            if forum.permissions_for(guild.me).read_messages:
                accessible_forums.append(forum)

        # Collect all threads from forums
        all_threads = []
        for forum in accessible_forums:
            try:
                # Get active threads
                for thread in forum.threads:
                    if thread.permissions_for(guild.me).read_messages:
                        all_threads.append(thread)

                # Get archived threads
                async for thread in forum.archived_threads(limit=None):
                    if thread.permissions_for(guild.me).read_messages:
                        all_threads.append(thread)
            except:
                continue

        # Combine all channels and threads
        all_channels = accessible_channels + all_threads
        total_channels = len(all_channels)

        # Debug info
        print(f"\nCounting messages for {user.name} in {guild.name}")
        print(f"Total channels to check: {len(accessible_channels)} text channels, {len(all_threads)} threads")

        if total_channels == 0:
            return 0

        # Process channels in batches for better performance
        batch_size = 5  # Reduced batch size for more frequent updates
        total_count = 0
        channels_processed = 0

        for i in range(0, total_channels, batch_size):
            batch = all_channels[i : i + batch_size]

            # Count messages in parallel for this batch
            tasks = []
            for channel in batch:
                # Create a task for each channel
                task = asyncio.create_task(self.count_channel_messages(channel, user, after_date, channel_completed_callback))
                tasks.append(task)

            # Wait for all tasks in this batch to complete
            counts = await asyncio.gather(*tasks, return_exceptions=True)

            # Sum up valid counts (handle any exceptions)
            for count in counts:
                if isinstance(count, int):
                    total_count += count

            channels_processed += len(batch)

            # Update progress
            if progress_callback:
                await progress_callback(channels_processed, total_channels)

        print(f"Total count for {user.name}: {total_count} messages\n")
        return total_count

    async def get_leaderboard_data(self, guild: discord.Guild, channel: discord.TextChannel) -> List[Tuple[str, int]]:
        """Get sorted leaderboard data for a guild by fetching message counts"""
        # Get all members in the guild
        members = [m for m in guild.members if not m.bot]
        total_users = len(members)

        # Get ALL actual channels we'll process (no estimation)
        all_channels_to_process = []

        # Add text channels and threads
        for ch in guild.channels:
            if isinstance(ch, (discord.TextChannel, discord.Thread)) and ch.permissions_for(guild.me).read_messages:
                all_channels_to_process.append(ch)

        # Add forum threads
        forum_channels = [
            ch for ch in guild.channels if isinstance(ch, discord.ForumChannel) and ch.permissions_for(guild.me).read_messages
        ]

        for forum in forum_channels:
            try:
                # Add active threads
                for thread in forum.threads:
                    if thread.permissions_for(guild.me).read_messages:
                        all_channels_to_process.append(thread)

                # Add archived threads
                async for thread in forum.archived_threads(limit=None):
                    if thread.permissions_for(guild.me).read_messages:
                        all_channels_to_process.append(thread)
            except:
                continue

        # Now we have the EXACT count
        total_channels_actual = len(all_channels_to_process)

        # Calculate total work units (users × channels)
        total_channels_to_process = total_channels_actual * total_users
        channels_processed = 0

        # Create a loading embed
        loading_embed = discord.Embed(
            title="📊 Message Leaderboard",
            description=f"Fetching message counts for all users...\nTotal channels to process: {total_channels_to_process}",
            color=discord.Color.gold(),
        )
        loading_embed.add_field(name="Overall Progress", value="0%", inline=True)
        loading_embed.add_field(name="Users Completed", value="0 / " + str(total_users), inline=True)
        loading_embed.add_field(
            name="Channels Processed",
            value="0 / " + str(total_channels_to_process),
            inline=True,
        )
        loading_embed.add_field(name="Processing", value="Starting...", inline=True)

        # Send loading message to the command channel
        loading_msg = await channel.send(embed=loading_embed)

        # Track progress
        completed_users = 0
        work_lock = asyncio.Lock()
        last_update_time = 0
        UPDATE_INTERVAL = 0.5  # Update display at most every 0.5 seconds

        async def increment_work_units():
            nonlocal channels_processed, last_update_time
            should_update = False
            async with work_lock:
                channels_processed += 1
                current_time = asyncio.get_event_loop().time()
                if current_time - last_update_time >= UPDATE_INTERVAL:
                    last_update_time = current_time
                    should_update = True

            # Call update outside of the lock to avoid deadlock
            if should_update:
                await update_progress_display()

        async def update_progress_display():
            nonlocal channels_processed
            # Read values while holding the lock
            async with work_lock:
                progress_percent = (
                    int((channels_processed / total_channels_to_process) * 100) if total_channels_to_process > 0 else 0
                )
                # Cap progress at 100% to avoid confusion
                progress_percent = min(progress_percent, 100)
                current_completed = completed_users
                current_processed = channels_processed

            # Update embed fields without holding the lock
            loading_embed.set_field_at(0, name="Overall Progress", value=f"{progress_percent}%", inline=True)
            loading_embed.set_field_at(
                1,
                name="Users Completed",
                value=f"{current_completed} / {total_users}",
                inline=True,
            )
            loading_embed.set_field_at(
                2,
                name="Channels Processed",
                value=f"{current_processed} / {total_channels_to_process}",
                inline=True,
            )
            try:
                await loading_msg.edit(embed=loading_embed)
            except:
                pass

        # Process users one at a time
        async def process_user(member):
            """Process a single user and return their count"""
            nonlocal completed_users
            count = await self.get_user_message_count(guild, member, None, None, increment_work_units)

            # Increment completed users
            async with work_lock:
                completed_users += 1

            # Update display after each user completes
            await update_progress_display()

            if count > 0:
                return (str(member.id), count)
            return None

        # Get message counts for all members
        message_counts = []

        # Process one user at a time
        for i, member in enumerate(members):
            # Update which user is being processed
            loading_embed.set_field_at(
                3,
                name="Processing",
                value=f"User {i + 1} of {total_users}: {member.display_name}",
                inline=True,
            )
            try:
                await loading_msg.edit(embed=loading_embed)
            except:
                pass

            # Process single user
            result = await process_user(member)
            if result:
                message_counts.append(result)

        # Update to show we're finalizing
        try:
            loading_embed.clear_fields()
            loading_embed.description = "All users processed! Preparing final leaderboard..."
            loading_embed.add_field(name="Status", value="✅ Sorting results...", inline=False)
            loading_embed.add_field(name="Users Processed", value=f"{total_users} users", inline=True)
            loading_embed.add_field(
                name="Total Channels Processed",
                value=f"{channels_processed} channels",
                inline=True,
            )
            loading_embed.add_field(
                name="Users with Messages",
                value=f"{len(message_counts)} users",
                inline=True,
            )
            await loading_msg.edit(embed=loading_embed)
        except:
            pass

        # Sort by message count
        sorted_results = sorted(message_counts, key=lambda x: x[1], reverse=True)

        # Delete loading message
        try:
            await loading_msg.delete()
        except:
            pass

        return sorted_results

    # Prefix command for leaderboard
    @commands.command(name="leaderboard", aliases=["lb", "top"])
    async def leaderboard_prefix(self, ctx: commands.Context):
        """Display the message count leaderboard for this server"""
        await self.show_leaderboard(ctx, ctx.guild, ctx.channel)

    # Slash command for leaderboard
    @app_commands.command(
        name="leaderboard",
        description="Display the message count leaderboard for this server",
    )
    async def leaderboard_slash(self, interaction: discord.Interaction):
        """Slash command to display the message count leaderboard"""
        await self.show_leaderboard(interaction, interaction.guild, interaction.channel)

    @app_commands.command(
        name="lb",
        description="Display the message count leaderboard for this server",
    )
    async def leaderboard_lb_slash(self, interaction: discord.Interaction):
        """Slash alias for leaderboard"""
        await self.show_leaderboard(interaction, interaction.guild, interaction.channel)

    @app_commands.command(
        name="top",
        description="Display the message count leaderboard for this server",
    )
    async def leaderboard_top_slash(self, interaction: discord.Interaction):
        """Slash alias for leaderboard"""
        await self.show_leaderboard(interaction, interaction.guild, interaction.channel)

    # Common method for both prefix and slash commands
    async def show_leaderboard(self, ctx_or_interaction, guild: discord.Guild, channel: discord.TextChannel):
        """Display the leaderboard for a guild"""
        # Get message counts for this guild
        sorted_users = await self.get_leaderboard_data(guild, channel)

        if not sorted_users:
            embed = discord.Embed(
                title="📊 Message Leaderboard",
                description="No message data available.",
                color=discord.Color.gold(),
            )
            if isinstance(ctx_or_interaction, discord.Interaction):
                await ctx_or_interaction.response.send_message(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)
            return

        # Create paginated view
        view = LeaderboardView(sorted_users)
        view.update_buttons()

        # Send initial embed with view
        if isinstance(ctx_or_interaction, discord.Interaction):
            await ctx_or_interaction.response.send_message(embed=view.get_embed(), view=view)
        else:
            await ctx_or_interaction.send(embed=view.get_embed(), view=view)

    # Prefix command for message count
    @commands.command(name="messagecount", aliases=["mc", "mycount"])
    async def message_count_prefix(self, ctx: commands.Context, member: discord.Member = None):
        """Check message count for yourself or another member"""
        if member is None:
            member = ctx.author

        await self.show_message_count(ctx, ctx.guild, member)

    # Slash command for message count
    @app_commands.command(
        name="messagecount",
        description="Check message count for yourself or another member",
    )
    @app_commands.describe(member="The member to check message count for (defaults to yourself)")
    async def message_count_slash(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        """Slash command to check message count"""
        if member is None:
            member = interaction.user

        await self.show_message_count(interaction, interaction.guild, member)

    @app_commands.command(
        name="mc",
        description="Check message count for yourself or another member",
    )
    @app_commands.describe(member="The member to check message count for (defaults to yourself)")
    async def message_count_mc_slash(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        """Slash alias for message count"""
        if member is None:
            member = interaction.user

        await self.show_message_count(interaction, interaction.guild, member)

    @app_commands.command(
        name="mycount",
        description="Check message count for yourself or another member",
    )
    @app_commands.describe(member="The member to check message count for (defaults to yourself)")
    async def message_count_mycount_slash(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        """Slash alias for message count"""
        if member is None:
            member = interaction.user

        await self.show_message_count(interaction, interaction.guild, member)

    # Common method for both prefix and slash commands
    async def show_message_count(self, ctx_or_interaction, guild: discord.Guild, member: discord.Member):
        """Display message count for a member"""
        # Send loading message
        loading_embed = discord.Embed(
            title="📈 Message Count",
            description=f"Fetching message count for {member.display_name}...",
            color=member.color,
        )
        if isinstance(ctx_or_interaction, discord.Interaction):
            await ctx_or_interaction.response.send_message(embed=loading_embed)
        else:
            loading_msg = await ctx_or_interaction.send(embed=loading_embed)

        # Get message count
        count = await self.get_user_message_count(guild, member, None, None, None)

        # Get rank by fetching all counts
        all_counts = await self.get_leaderboard_data(guild, ctx_or_interaction.channel)
        rank = 0
        for i, (uid, _) in enumerate(all_counts, 1):
            if uid == str(member.id):
                rank = i
                break

        # Create final embed
        embed = discord.Embed(title="📈 Message Count", color=member.color)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="Messages", value=f"**{count:,}**", inline=True)
        if rank > 0:
            embed.add_field(name="Rank", value=f"**#{rank}**", inline=True)

        # Update or send final message
        if isinstance(ctx_or_interaction, discord.Interaction):
            await ctx_or_interaction.edit_original_response(embed=embed)
        else:
            await loading_msg.edit(embed=embed)


async def setup_leaderboard(bot, guilds):
    cog = Leaderboard(bot)
    await bot.add_cog(cog, guilds=guilds)
