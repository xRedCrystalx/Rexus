import sys, discord, asyncio
sys.dont_write_bytecode = True
from discord.ext import commands
from src.connector import shared

from src.core.helpers.embeds import create_base_embed, apply_embed_items
from src.core.helpers.errors import report_error
from src.core.helpers.emojis import CustomEmoji as CEmoji

from xRedUtils.type_hints import SIMPLE_ANY

class ReactionFilter:
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot: commands.AutoShardedBot = bot
    
        self.counter: int = 0
        self.blacklist: list[str] = ["🖕", "🍌", "🍑", "🍆", "🥵", "😩", "🤤", "💦"]
        self.db: dict[int, dict[str, discord.Message | dict[int, int] | list[str]] | discord.TextChannel] = {}

    async def check_reaction(self, guild_db: dict[str, SIMPLE_ANY], payload: discord.RawReactionActionEvent, **OVERFLOW) -> None:
        if guild_db["reaction"]["status"] and payload.member and guild_db["reaction"]["status"] and (emoji := str(payload.emoji)):
            if emoji not in self.blacklist:
                return

            if not self.db.get(payload.message_id):
                self.db[payload.message_id] = {"msg" : None, "users" : {}, "emojis" : [], "channel" : payload.member.guild.get_channel(payload.channel_id)}

            if not (emoji in self.db[payload.message_id]["emojis"]):
                self.db[payload.message_id]["emojis"].append(emoji)

            if self.db[payload.message_id]["users"].get(payload.member.id):
                self.db[payload.message_id]["users"][payload.member.id] += 1
            else:
                self.db[payload.message_id]["users"][payload.member.id] = 1

            if (log_channnel_id := guild_db["reaction"]["log_channel"]):
                embed: discord.Embed = apply_embed_items(
                    embed=create_base_embed("Reaction Filter"),
                    thumbnail=payload.member.display_avatar.url,
                    footer="Reaction will be removed.")
                embed.add_field(name="`` Member ``", value=f"{CEmoji.PROFILE}┇{payload.member.display_name}\n{CEmoji.GLOBAL}┇{payload.member.name}\n{CEmoji.ID}┇{payload.member.id}", inline=True)
                embed.add_field(name="`` Rule ``", value=f"User reacted with {payload.emoji} emoji under https://discord.com/channels/{payload.guild_id}/{payload.channel_id}/{payload.message_id}.", inline=True)

                if log_channel := payload.member.guild.get_channel(log_channnel_id):
                    await log_channel.send(embed=embed)

    async def update(self, message_id: int) -> None:
        try:
            if msg_db := self.db.get(message_id):
                if not msg_db.get("msg"):
                    if message := await msg_db["channel"].fetch_message(message_id):
                        self.db[message_id]["msg"] = message
                    else:
                        return self.db.pop(message_id)

                message: discord.Message = msg_db["msg"]
                guild_db: dict[str, SIMPLE_ANY] = shared.db.load_data(message.guild.id)

                for emoji in self.db[message_id]["emojis"].copy():
                    await message.clear_reaction(emoji=emoji)
                    self.db[message_id]["emojis"].remove(emoji)

                if (role_id := guild_db["reaction"]["reactionBanRole"]) and role_id in [role.id for role in message.guild.roles]:
                    for user_id, counter in self.db[message_id]["users"].copy().items():
                        if counter >= 5 and (member := message.guild.get_member(user_id)):
                            if role_id not in [role.id for role in member.roles]:
                                await member.add_roles(discord.Object(role_id))

                            if log_channel_id := guild_db["reaction"]["log_channel"]:
                                embed: discord.Embed = apply_embed_items(
                                    embed=create_base_embed("Reaction Ban"),
                                    thumbnail=member.display_avatar.url,
                                    footer="Sucessfully reaction banned the user.")                          
                                embed.add_field(name="`` Member ``", value=f"{CEmoji.PROFILE}┇{member.display_name}\n{CEmoji.GLOBAL}┇{member.name}\n{CEmoji.ID}┇{member.id}", inline=True)

                                if log_channel := message.guild.get_channel(log_channel_id):
                                    await log_channel.send(embed=embed)

                        self.db[message_id]["users"].pop(user_id)
        except Exception:
            await report_error(self.update, "full")

    async def background_clock(self) -> None:
        while True:
            self.counter += 1
            for message in self.db.copy():
                shared.loop.create_task(self.update(message))

            if self.counter >= 2000:
                self.db = {}
                self.counter = 0
            await asyncio.sleep(2.5)

SAVE: list[str] = ["db", "counter"]
async def setup(bot: commands.AutoShardedBot) -> None:
    """await shared.module_manager.load(reaction := ReactionFilter(bot), tasks=[reaction.background_clock],
        config={
            reaction.check_reaction: ["on_raw_reaction_add"]
        }
    )
"""