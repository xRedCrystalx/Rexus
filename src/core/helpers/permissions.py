import sys
sys.dont_write_bytecode = True
from discord import Permissions, ChannelType, Role
import src.connector as con

from typing import Literal
from xRedUtils.iterables import compare_iterables, get_attr_data

class Permission:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared
        
    def check_roles(self, required_roles: list[int | Role], member_roles: list[int | Role]) -> list[int]:
        return compare_iterables(get_attr_data(required_roles, "id"), get_attr_data(member_roles, "id"))
    
    def check_permissions(self, current_perms: list[Permissions], required_perms: ...) -> list[Permissions]:
        required_perms = [getattr(Permissions, perm, None) for perm in required_perms]
        return compare_iterables(required_perms, current_perms)

    def check_channel_type(self, current_location: ChannelType, required_location: Literal["text", "category", "forum", "group", "news", "news_thread", "private", "private_thread", "public_thread", "voice", "stage_voice"]) -> bool:
        return current_location == getattr(ChannelType, required_location, None)
    
    def check_id(self, current: object | int, required: int) -> bool:
        return getattr(current, "id", current) == required