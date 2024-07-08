import sys, typing
sys.dont_write_bytecode = True
from discord import Permissions, ChannelType, Member
from discord.abc import GuildChannel, PrivateChannel
from src.connector import shared

from xRedUtilsAsync.iterables import compare_iterables, get_attr_data, to_iterable

async def check_ids(ids1: list[int | object], ids2: list[int | object]) -> list[int]:
    return await compare_iterables(
        await get_attr_data(await to_iterable(ids1), "id"),
        await get_attr_data(await to_iterable(ids2), "id")
    )

# More brainstorming required
async def check_permissions(current_perms: list[Permissions], required_perms: ...) -> list[Permissions]:
    raise NotImplementedError()

    return await compare_iterables(
        [getattr(Permissions, perm, None) for perm in required_perms],
        current_perms)

async def check_channel_type(current_location: GuildChannel | PrivateChannel | ChannelType, required_location: typing.Literal["text", "category", "forum", "group", "news", "news_thread", "private", "private_thread", "public_thread", "voice", "stage_voice"]) -> bool:
    current_location = current_location if isinstance(current_location, ChannelType) else getattr(current_location, "type", None)
    return current_location == getattr(ChannelType, required_location, None)

async def isGuildAdministrator(member: Member) -> bool:
    return member.guild_permissions.administrator or (member.id == member.guild.owner.id)

async def isBotAdministrator(member: Member | int) -> bool:
    return (member if isinstance(member, int) else member.id) in shared.db.load_data().get("owners")