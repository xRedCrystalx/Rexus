import sys
sys.dont_write_bytecode = True
from typing import override, Self
from src.connector import shared, Shared

from discord.ext.commands import Cog
from xRedUtils.objects import get_full_object_path


class BaseTemplate:
    def __init__(self, id: str) -> None:
        self.shared: Shared = shared
        self._type: str = "base"
        self._full_self_path: str = get_full_object_path(self)
        self.ID: str = id

    async def build(self, *args, **kwargs) -> Self:
        return self

    async def terminate(self, *args, **kwargs) -> None:
        return

#d                               Actual templates                                           

class DiscordTemplate(Cog, BaseTemplate):
    def __init__(self, id: str) -> None:
        super().__init__(id)

        self._type = "discord"

class PluginTemplate(BaseTemplate):
    def __init__(self, id: str) -> None:
        super().__init__(id)

        self._type = "plugin"

class SystemTemplate(BaseTemplate):
    def __init__(self, id: str) -> None:
        super().__init__(id)
        
        self._type = "system"
        self._var: str = None

    @override
    async def build(self, config: dict[str, str], *args, **kwargs) -> Self:
        self._var = config.get("var")
        return self
