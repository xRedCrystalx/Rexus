
import sys, discord
sys.dont_write_bytecode = True
from src.connector import shared

from xRedUtils.type_hints import SIMPLE_ANY

class AutoMod:
    async def response(self, action: discord.AutoModAction, guild_db: dict[str, SIMPLE_ANY], **OVERFLOW) -> None:
        if action.action.channel_id and guild_db["automod"]["status"]:
            system_channel: discord.TextChannel = action.guild.get_channel(action.action.channel_id)
            db_rule_data: dict | str | None = guild_db["automod"]["rules"].get(str(action.rule_id))

            if db_rule_data and system_channel:
                frmt: dict[str, object] = {"user": action.member, "channel": action.channel}

                if isinstance(db_rule_data, dict):
                    if (data := db_rule_data.get(action.matched_keyword) or db_rule_data.get("GLOBAL_VALUE")):
                        await system_channel.send(str(data).format(**frmt))

                elif isinstance(db_rule_data, str):
                    await system_channel.send(db_rule_data.format(**frmt))
        return None
    
async def setup(bot) -> None:
    await shared.add_plugin(AutoMod, 
        config={
            ["on_automod_action"]: AutoMod.response
        }
    )
