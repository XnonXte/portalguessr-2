from typing import Optional
import discord
from discord.ext import commands
from discord import app_commands
from utils.game.lb import get_statistic, get_statistics
from hooks.discord.make_embed import make_embed
from hooks.discord.get_user_mention import get_user_mention
from hooks.discord.get_user import get_user
from hooks.python.use_enumerate import use_enumerate
from utils.bot.make_icon import make_icon
from config import BOT_ACCENT_COLOR, MAX_REQUEST_ENTRIES, DEFAULT_REQUEST_ENTRIES


class Leaderboard(commands.Cog):
    """Cog for leaderboard related command.

    Args:
        commands (commands.Bot): The bot's instance.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="lb", description="Shows the current leaderboard.")
    @app_commands.describe(
        user="Targets a user the current server in the leaderboard",
        user_id="Targets a user in the leaderboard by their Discord's id.",
        skip="Skip to the given number (defaults to 1).",
        limit=f"The total amount that needs to be displayed (defaults to {DEFAULT_REQUEST_ENTRIES}, {MAX_REQUEST_ENTRIES} maximum)",
    )
    async def lb(
        self,
        ctx,
        user: Optional[discord.User] = None,
        user_id: Optional[str] = None,
        skip: Optional[int] = 1,
        limit: Optional[int] = DEFAULT_REQUEST_ENTRIES,
    ):
        await ctx.defer()
        if user:
            statistic = await get_statistic(user.id)
            if statistic == None:
                raise commands.UserNotFound(user.id)
            else:
                easy, medium, hard, veryhard = statistic["scores"].values()
                elo = sum([easy * 3, medium * 5, hard * 10, veryhard * 15])
                started_at = statistic["createdStamp"]

                embed = make_embed(
                    description=f"{user.mention} stats",
                    color=user.accent_color or BOT_ACCENT_COLOR,
                )
                embed.add_field(name="ELO", value=elo, inline=False)
                embed.add_field(name="Easy", value=easy, inline=False)
                embed.add_field(name="Medium", value=medium, inline=False)
                embed.add_field(name="Hard", value=hard, inline=False)
                embed.add_field(name="Very Hard", value=veryhard, inline=False)
                embed.add_field(
                    name="Started at", value=f"<t:{started_at}:f>", inline=False
                )
                embed.set_footer(
                    text="Keep playing to improve your stats!",
                    icon_url="attachment://icon.png",
                )
                embed.set_author(name=user.name, icon_url=user.avatar.url)
                await ctx.send(embed=embed, file=make_icon())
        elif user_id:
            statistic = await get_statistic(user_id)
            if statistic == None:
                raise commands.UserNotFound(user_id)
            else:
                target_user = await get_user(self.bot, user_id)
                target_user_mention = await get_user_mention(self.bot, user_id)
                target_user_color = (
                    target_user.accent_color
                    if target_user != None
                    else BOT_ACCENT_COLOR
                )
                target_user_name = target_user.name if target_user != None else "N/A"
                target_user_avatar = (
                    target_user.avatar.url
                    if target_user != None
                    else "attachment://icon.png"
                )
                easy, medium, hard, veryhard = statistic["scores"].values()
                elo = sum([easy * 3, medium * 5, hard * 10, veryhard * 15])
                started_at = statistic["createdStamp"]
                embed = make_embed(
                    description=f"{target_user_mention} stats",
                    color=target_user_color,
                )
                embed.add_field(name="ELO", value=elo, inline=False)
                embed.add_field(name="Easy", value=easy, inline=False)
                embed.add_field(name="Medium", value=medium, inline=False)
                embed.add_field(name="Hard", value=hard, inline=False)
                embed.add_field(name="Very Hard", value=veryhard, inline=False)
                embed.add_field(
                    name="Started at", value=f"<t:{started_at}:f>", inline=False
                )
                embed.set_footer(
                    text="Keep playing to improve your stats!",
                    icon_url="attachment://icon.png",
                )
                embed.set_author(name=target_user_name, icon_url=target_user_avatar)
                await ctx.send(embed=embed, file=make_icon())
        else:
            if limit > MAX_REQUEST_ENTRIES:
                await ctx.send(
                    f"Exceeded the maximum value for amount! The maximum value is {MAX_REQUEST_ENTRIES}",
                    ephemeral=True,
                )

                return
            elif limit <= 0:
                await ctx.send(
                    "The amount value can't be less than or equal to 0!", ephemeral=True
                )

                return
            if skip <= 0:
                await ctx.send(
                    "The starting number can't be less than or equal to 0!",
                    ephemeral=True,
                )

                return
            statistics = await get_statistics(skip, limit)
            statistics_length = len(statistics)
            statistic_entry = []

            async def callback(index, item):
                user_mention = await get_user_mention(self.bot, item["userId"])
                easy, medium, hard, veryhard = item["scores"].values()
                elo = sum([easy * 3, medium * 5, hard * 10, veryhard * 15])
                entry_message = f"{index}. {user_mention} at **{elo}** ELO"

                statistic_entry.append(entry_message)

            await use_enumerate(statistics, callback, skip)
            embed_description = "\n".join(statistic_entry) or "Empty :("
            embed_footer = (
                f"Showing {statistics_length} results | Skipping from {skip}"
                if skip != 1
                else f"Showing {statistics_length} results "
            )
            embed = make_embed(
                "Leaderboard",
                embed_description,
                BOT_ACCENT_COLOR,
            )
            embed.set_footer(
                text=embed_footer,
                icon_url="attachment://icon.png",
            )
            await ctx.send(embed=embed, file=make_icon())


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
