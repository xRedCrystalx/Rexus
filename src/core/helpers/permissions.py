import sys, typing
sys.dont_write_bytecode = True
from discord import Permissions, ChannelType
from src.connector import shared

from xRedUtils.iterables import compare_iterables, get_attr_data


def check_ids(ids1: list[int | object], ids2: list[int | object]) -> list[int]:
    if not isinstance(ids1, list):
        ids1 = [ids1]

    return compare_iterables(get_attr_data(ids1, "id"), get_attr_data(ids2, "id"))

def check_id(current: object | int, required: object | int) -> bool:
    return getattr(current, "id", current) == getattr(required, "id", required)

def check_permissions(current_perms: list[Permissions], required_perms: ...) -> list[Permissions]:
    required_perms = [getattr(Permissions, perm, None) for perm in required_perms]
    return compare_iterables(required_perms, current_perms)

def check_channel_type(current_location: ChannelType, required_location: typing.Literal["text", "category", "forum", "group", "news", "news_thread", "private", "private_thread", "public_thread", "voice", "stage_voice"]) -> bool:
    return current_location == getattr(ChannelType, required_location, None)

def check_bot_owner(member_id: int)-> bool:
    return member_id in shared.db.load_data().get("owners")