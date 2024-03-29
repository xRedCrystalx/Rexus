import discord, aiohttp, asyncio, typing
from discord.ext import commands
import src.connector as con


class Spy:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = self.shared.bot

    async def queue(self, bot_db: dict[str, typing.Any], guild_id: int, message: discord.Message = None, after: discord.Message = None, before: discord.Message = None, **OVERFLOW) -> None:
        try:
            if guild_id:
                if message:
                    if str(message.guild.id) in bot_db["spy"].keys():
                        self.shared.loop.create_task(self.webhook_handler(message, bot_db["spy"][guild_id]))
                else:
                    if after and before:
                        if str(after.guild.id) in bot_db["spy"].keys():
                            self.shared.loop.create_task(self.bot_edit_handler(before, after, bot_db["spy"][guild_id]))

        except Exception as error:
            self.shared.logger.log(f"@Spy.queue: {type(error).__name__}: {error}", "ERROR")
        return None

    async def webhook_handler(self, message: discord.Message, bot_db: dict[str, typing.Any]) -> None:
        try:
            for output, input in bot_db.items():
                if message.channel.id in input and output.startswith("https://"):
                    async with aiohttp.ClientSession() as session:
                        webhook: discord.Webhook = discord.Webhook.from_url(url=output, session=session)
                        await webhook.send(username=f"{message.author.display_name} in {message.channel.name}", avatar_url=message.author.display_avatar.url,
                                    content=message.clean_content,
                                    files=[await x.to_file(filename=x.filename, description=x.description) for x in message.attachments],
                                    embeds=message.embeds)
        except Exception as error:
            self.shared.logger.log(f"@Spy.webhook_handler: {type(error).__name__}: {error}", "ERROR")
        return None

    async def bot_edit_handler(self, before: discord.Message, after: discord.Message, bot_db: dict[str, list[int]]) -> None:
        try:
            channel_id: int | None = None
            
            for log_id, targeted_channels in bot_db.items():
                if after.channel.id in targeted_channels:
                    channel_id = int(log_id)
                    break

            if not channel_id:
                return None

            if not (channel := self.bot.get_channel(channel_id)):
                return None

            async for old_message in channel.history(limit=25):
                if old_message.content == before.content:
                    return await self.shared.sender.resolver([{old_message : {"action" : "edit", "kwargs" : {"content" : after.content}}}])
        
        except Exception as error:
            self.shared.logger.log(f"@Spy.bot_edit_handler: {type(error).__name__}: {error}", "ERROR")
        return None
