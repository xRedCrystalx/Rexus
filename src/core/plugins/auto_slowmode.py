import discord, asyncio, sys
sys.dont_write_bytecode = True
from discord.ext import commands
from src.connector import shared

from src.core.helpers.embeds import create_base_embed
from src.core.helpers.errors import report_error
from src.core.helpers.emojis import CustomEmoji as CEmoji

from xRedUtilsAsync.times import seconds_to_str
from xRedUtilsAsync.type_hints import SIMPLE_ANY

class AutoSlowmode:
    def __init__(self, bot: commands.AutoShardedBot, interval_minutes: int = 5) -> None:
        self.bot: commands.AutoShardedBot = bot

        self.slowmode_rules: dict[int, tuple[int, int]] = {
            5: (15, 60),
            10: (60, 130),
            15: (130, 250),
            20: (250, 400),
            30: (400, 750)
        }
        self.interval_minutes: int = interval_minutes
        self.database: dict = {}

    async def message_listener(self, guild_db: dict[str, SIMPLE_ANY], message: discord.Message, **OVERFLOW) -> None:
        if guild_db["auto_slowmode"]["status"] and str(message.channel.id) in guild_db["auto_slowmode"]["monitored"]:

            if self.database.get(message.channel.id):
                self.database[message.channel.id] += 1

                if message.channel.slowmode_delay <= 10:
                    if self.database[message.channel.id] > 100:
                        shared.logger.log("TESTING", f"@AutoSlowmode.message_listener > Forcing slowmode. > 100 messages.")
                        await self.slowmode(channel=message.channel)
            else:
                self.database[message.channel.id] = 1

    async def slowmode(self, channel: discord.TextChannel) -> None:
        guild_db: dict[str, SIMPLE_ANY] = shared.db.load_data(channel.guild.id)

        default_delay: int = guild_db["auto_slowmode"]["monitored"].get(str(channel.id))
        if not default_delay or default_delay > 21600:
            default_delay = 10

        numMsg: int | float = (self.database[channel.id] / self.interval_minutes) * channel.slowmode_delay
        total: int | float = numMsg - (numMsg * 20 / 100)
        shared.logger.log("NP_DEBUG", f"@AutoSlowmode.slowmode > Message count: {total}.")

        for time, (smaller, bigger) in self.slowmode_rules.items():
            if total >= smaller and total < bigger:
                delay: int = time
                break
        else:
            delay = default_delay if total < 15 else 60

        await shared.logger.log("NP_DEBUG", f"@AutoSlowmode.slowmode > Got delay: {delay}.")

        if guild_db["auto_slowmode"]["status"] and (channel.slowmode_delay != delay and delay >= default_delay):
            await channel.edit(slowmode_delay=delay)

            if (log_channel_id := guild_db["auto_slowmode"]["log_channel"]):
                embed: discord.Embed = create_base_embed("Auto Slowmode")
                embed.add_field(name="`` Channel ``", value=f"{CEmoji.TEXT_C}┇{channel.mention}\n{CEmoji.ID}┇{channel.id}", inline=True)
                embed.add_field(name="`` Change ``", value=f"**Slowmode delay:**\n`{await seconds_to_str(channel.slowmode_delay)}` ➔ `{await seconds_to_str(delay)}`", inline=True)

                if (log_channel := channel.guild.get_channel(log_channel_id)):
                    await log_channel.send(embed=embed)

    async def background_clock(self) -> None:
        while True:
            await asyncio.sleep(self.interval_minutes * 60)

            for channel_id in self.database.keys():
                try:
                    if channel := self.bot.get_channel(channel_id):
                        await self.slowmode(channel=channel)
                except Exception:
                    await report_error(self.background_clock, "full")

            self.database.clear()

async def setup(bot: commands.AutoShardedBot) -> None:
    await shared.add_plugin(AutoSlowmode(bot), tasks=[AutoSlowmode.background_clock],
        config={
            AutoSlowmode.message_listener: ["on_message"]
        }
    )
