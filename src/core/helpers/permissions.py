import sys, typing
sys.dont_write_bytecode = True
from discord import Permissions, ChannelType, Role
from src.connector import shared

from xRedUtils.iterables import compare_iterables, get_attr_data


def check_roles(required_roles: list[int | Role], member_roles: list[int | Role]) -> list[int]:
    if not isinstance(required_roles, list):
        required_roles = [required_roles]

    return compare_iterables(get_attr_data(required_roles, "id"), get_attr_data(member_roles, "id"))

def check_permissions(current_perms: list[Permissions], required_perms: ...) -> list[Permissions]:
    required_perms = [getattr(Permissions, perm, None) for perm in required_perms]
    return compare_iterables(required_perms, current_perms)

def check_channel_type(current_location: ChannelType, required_location: typing.Literal["text", "category", "forum", "group", "news", "news_thread", "private", "private_thread", "public_thread", "voice", "stage_voice"]) -> bool:
    return current_location == getattr(ChannelType, required_location, None)

def check_id(current: object | int, required: object | int) -> bool:
    return getattr(current, "id", current) == getattr(required, "id", required)

def check_bot_owner(member_id: int)-> bool:
    return member_id in shared.db.load_data().get("owners")