import discord, asyncio, sys, typing
sys.dont_write_bytecode = True
import src.connector as con
from xRedUtils.dates import get_datetime
from xRedUtils.times import seconds_to_str

if typing.TYPE_CHECKING:
    from discord.ext import commands

class AutoSlowmode:
    def __init__(self, interval_minutes: int = 5) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = self.shared.bot

        self.slowmode_rules: dict[int, tuple[int, int]] = {
            5: (15, 60),
            10: (60, 130),
            15: (130, 250),
            20: (250, 400),
            30: (400, 750)
        }
        self.interval_minutes: int = interval_minutes
        self.database: dict = {}

    async def message_listener(self, guild_db: dict[str, typing.Any], message: discord.Message, **OVERFLOW) -> None:
        if str(message.channel.id) in guild_db["auto_slowmode"]["monitored"] and guild_db["auto_slowmode"]["status"]:

            if self.database.get(message.channel.id):
                self.database[message.channel.id] += 1

                if message.channel.slowmode_delay <= 10:
                    if self.database[message.channel.id] > 100:
                        self.shared.logger.log(f"@AutoSlowmode.message_listener > Forcing slowmode. > 100 messages.", "TESTING")
                        await self.slowmode(channel=message.channel)
            else:
                self.database[message.channel.id] = 1

    async def slowmode(self, channel: discord.TextChannel) -> None:
        guild_db: dict = self.shared.db.load_data(channel.guild.id)

        default_delay: int = guild_db["auto_slowmode"]["monitored"].get(str(channel.id))
        if not default_delay or default_delay > 21600:
            default_delay = 10

        numMsg: int | float = (self.database[channel.id] / self.interval_minutes) * channel.slowmode_delay
        total: int | float = numMsg - (numMsg * 20 / 100)
        self.shared.logger.log(f"@AutoSlowmode.slowmode > Message count: {total}.", "NP_DEBUG")

        for time, (smaller, bigger) in self.slowmode_rules.items():
            if total >= smaller and total < bigger:
                delay: int = time
                break
        else:
            delay = default_delay if total < 15 else 60

        self.shared.logger.log(f"@AutoSlowmode.slowmode > Got delay: {delay}.", "NP_DEBUG")

        if channel.slowmode_delay != delay and delay >= default_delay and guild_db["auto_slowmode"]["status"]:
            self.shared.sender.resolver(con.Event(channel, "edit", event_data={"kwargs": {"slowmode_delay": delay}}))

            if (log_channel_id := guild_db["auto_slowmode"]["log_channel"]):
                embed: discord.Embed = discord.Embed(title="Auto Slowmode", color=discord.Colour.dark_embed(), timestamp=get_datetime())
                embed.add_field(name="`` Channel ``", value=f"<:text_c:1203423388320669716>┇{channel.mention}\n<:ID:1203410054016139335>┇{channel.id}", inline=True)
                embed.add_field(name="`` Change ``", value=f"**Slowmode delay:**\n`{seconds_to_str(channel.slowmode_delay)}` ➔ `{seconds_to_str(delay)}`", inline=True)

                if (log_channel := channel.guild.get_channel(log_channel_id)):
                    self.shared.sender.resolver(con.Event(log_channel, "send", event_data={"kwargs": {"embed" : embed}}))

    async def start(self) -> None:
        while True:
            await asyncio.sleep(self.interval_minutes * 60)
            self.shared.logger.log(f"@AutoSlowmode.start > Executing {self.interval_minutes} min loop.", "NP_DEBUG")

            for channel_id in self.database:
                try:
                    if channel := self.bot.get_channel(channel_id):
                        await self.slowmode(channel=channel)
                except Exception:
                    self.shared.logger.log(f"@AutoSlowmode.start > {self.shared.errors.full_traceback()}", "ERROR")

            self.database.clear()
