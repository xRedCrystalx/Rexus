import discord, asyncio, sys, typing
sys.dont_write_bytecode = True
import src.connector as con

if typing.TYPE_CHECKING:
    from discord.ext import commands

class AutoSlowmode:
    def __init__(self, interval_minutes: int = 5) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = self.shared.bot
        self.interval_minutes: int = interval_minutes
        self.loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()

        self.database: dict = {}

    async def message_listener(self, message: discord.Message, guild_db: dict[str, typing.Any], **OVERFLOW) -> None:
        if message.channel.id in guild_db["auto_slowmode"]["monitored"] and guild_db["auto_slowmode"]["status"]:
            if self.database.get(message.channel.id):
                self.database[message.channel.id] += 1
                
                if message.channel.slowmode_delay <= 10:
                    if self.database[message.channel.id] > 100:
                        await self.slowmode(channel=message.channel)
                        self.database.pop(message.channel.id)
            else:
                self.database[message.channel.id] = 1

    async def slowmode(self, channel: discord.TextChannel) -> None:
        guild_db: dict = self.shared.db.load_data(channel.guild.id)
        
        async def slowmode_handler(newTimeout: int) -> None:
            if channel.slowmode_delay != newTimeout and guild_db["auto_slowmode"]["status"]:
                await self.shared.sender.resolver([{channel : {"action" : "edit", "kwargs" : {"slowmode_delay" : newTimeout}}}])
                
                if (channel_id := guild_db["auto_slowmode"]["log_channel"]):
                    embed: discord.Embed=discord.Embed(title="AutoSlowmode", color=discord.Colour.dark_embed(), timestamp=self.shared._datetime())
                    embed.add_field(name="`` Channel ``", value=f"**Channeč Name:** {channel.name}\n**Channel ID:** {channel.id}", inline=True)
                    embed.add_field(name="`` Change ``", value=f"Value change:\n`{channel.slowmode_delay}s` ➔ `{newTimeout}s`", inline=True)
                    embed.set_footer(text=f"Channel ID: {channel.id}")
                    
                    if channel := self.bot.get_channel(channel_id):
                        await self.shared.sender.resolver([{channel: {"action" : "send", "kwargs" : {"embed" : embed}}}])

        numMsg: int | float = (self.database[channel.id] / 5) * channel.slowmode_delay
        total: int | float = numMsg - (numMsg * 20 / 100)

        if total > 0 and total <= 60:
            await slowmode_handler(newTimeout=5)
        elif total > 60 and total <= 130:
            await slowmode_handler(newTimeout=10)
        elif total > 130 and total <= 250:
            await slowmode_handler(newTimeout=15)
        elif total > 250 and  total <= 400:
            await slowmode_handler(newTimeout=20)
        elif total > 400 and total <= 750:
            await slowmode_handler(newTimeout=30)
        elif total > 750:
            await slowmode_handler(newTimeout=60)
            
    async def start(self) -> None:
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            await asyncio.sleep(self.interval_minutes * 60)

            for channel_id in self.database:
                channel: discord.TextChannel = self.bot.get_channel(channel_id)
                self.loop.create_task(self.slowmode(channel=channel))

            self.database.clear()
