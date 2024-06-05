import sys
sys.dont_write_bytecode = True
from discord.ext import commands
from discord import Permissions, ChannelType, Role

from typing import Literal
import src.connector as con

from xRedUtils.iterables import compare_iterables

class Permission:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.AutoShardedBot = self.shared.bot
        
    def check_roles(self, required_roles: list[int | Role], member_roles: list[int | Role]) -> list[int]:
        required_roles = [role if isinstance(role, int) else role.id for role in required_roles]
        member_roles = [role if isinstance(role, int) else role.id for role in member_roles]
        return compare_iterables(required_roles, member_roles)
    
    def check_permissions(self, current_perms: list[Permissions], required_perms: ...) -> list[Permissions]:
        required_perms = [getattr(Permissions, perm, None) for perm in required_perms]
        return compare_iterables(required_perms, current_perms)

    def check_location(self, current_location: ChannelType, required_location: Literal["text", "category", "forum", "group", "news", "news_thread", "private", "private_thread", "public_thread", "voice", "stage_voice"]) -> bool:
        return current_location == getattr(ChannelType, required_location, None)