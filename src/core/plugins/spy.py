import discord, aiohttp, asyncio, typing
from discord.ext import commands
import src.connector as con


class Spy:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = self.shared.bot
        self.loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        self.webhook_handling: dict[str, tuple[int, ...]] = {
            "https://discord.com/api/webhooks/1141072905246085190/6Z2m5gZpWKJLLm-EZo09SjvpPrMzM16i3_GR22AZKWC5_ENcnaXUwv58EwW7Q0o39jDn" : (1114791447095414794, 1074191101763780648),                                           # announcements
            "https://discord.com/api/webhooks/1141075746928992297/VXUfVjIBROQ9IYA9T0rusjnBPgHMxWfrJ-t5raHvGyL4qf7l5PsqL3X84EM6cB_hPArh" : (1074188790610022412,),                                                               # general chat 
            "https://discord.com/api/webhooks/1141087452300316763/zWbxRmDfVE-vSt4MTs-5rhALkpoCqGhEhIqXsHWoBLKnlc0PoqNltomugvYfemxNulzM" : (1131048613267648532,),                                                               # mc chat
            "https://discord.com/api/webhooks/1141078861455564830/NqckE2EDttOKNAqjnIhiZBXWCXm3i7fiJ5DEp7FK22O7daXReGSzDNl2R260CVmZac06" : (1104999993695281252,),                                                               # images
            "https://discord.com/api/webhooks/1141086692758007839/0nBbtNZhjpRfWKnnlzKGmk6HxlVQVNCRAl0AB567LEqnLsXRdxGe0-A8nl_Wk1XZa8jx" : (1105956029398794280, 1105949196101615708),                                           # memeber cmds
            "https://discord.com/api/webhooks/1141086514722390076/GCiqTX1GTN98rPzOW8MpKKglf8v1_9lDhMrrnsMx8mCcjA5qJQlVGobt7uUd0w3Mu8BF" : (1104993674472988684, 1104993674472988684, 1074193519406743583, 1114790672336167012), # content
            "https://discord.com/api/webhooks/1141086842893119568/7A8hcpVBwElfX2m7-JGU-K988Kizxk4WxgIHkgI_6rh3XjswVWWElTH9i9DkiUIl1nh5" : (1127884899899150356, 1122300613569556510, 1133995408088109108, 1074192653438165063), # random useless
            "https://discord.com/api/webhooks/1141086972635533394/mxVwEXwZKuMPU5FyKRZTV7omu8cyQ9eMD1EHZm3HbzcVNYX61PubHAnyygxzwpRC97Pw" : (1105004801923764285,),                                                               # staff chat
            "https://discord.com/api/webhooks/1141087088977129482/cDqP_khQ0OYs0mpWTfrXarfvMfTOf9zKtamn44aav8RoabotiU3lkR0_Xi-ZlVJUH8_e" : (1124767738506793010, 1123083637022273546, 1127764368382247012),                      # staff logs important
            "https://discord.com/api/webhooks/1141087232783036566/soVFhLijtuUYo1qcfrrOVk2nP1f16wq3x8NbB0NKt_put79WRnWtAC9cPBwfA5KoTDYW" : (1124766971947384913,),                                                               # logs useless
            "https://discord.com/api/webhooks/1141087325254844496/pWwRMZe-qNIeQnUsdqK4YGXFIgewX0UtyMPNqqZ6NSv25uCelrPIPKzCmArwz-jYihyh" : (1074193221837668422,)                                                                # staff cmd
        }

    async def queue(self, bot_db: dict[str, typing.Any], guild_id: int, message: discord.Message = None, after: discord.Message = None, before: discord.Message = None, **OVERFLOW) -> None:
        try:
            if guild_id:
                if message:
                    if str(message.guild.id) in bot_db["spy"].keys():
                        self.loop.create_task(self.webhook_handler(message, bot_db["spy"][guild_id]))
                else:
                    if after and before:
                        if str(after.guild.id) in bot_db["spy"].keys():
                            self.loop.create_task(self.bot_edit_handler(before, after, bot_db["spy"][guild_id]))

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
                if str(after.channel.id) in targeted_channels:
                    channel_id = int(log_id)
                    break
            
            if not channel_id:
                return None
            
            channel: discord.TextChannel = self.bot.get_channel(channel_id)
            if not channel:
                return None

            async for old_message in channel.history(limit=50):
                if old_message.content == before.content:
                    return await self.shared.sender.resolver([{old_message : {"action" : "edit", "kwargs" : {"content" : after.content}}}])
        
        except Exception as error:
            self.shared.logger.log(f"@Spy.bot_edit_handler: {type(error).__name__}: {error}", "ERROR")
        return None
