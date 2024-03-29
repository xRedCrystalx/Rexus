import sys, discord, typing
sys.dont_write_bytecode = True
from discord import ui
from discord.ui import RoleSelect, UserSelect, MentionableSelect, ChannelSelect, Select

AllSelects: typing.TypeAlias = RoleSelect | UserSelect | MentionableSelect | ChannelSelect | Select

class SelectMenus:
    def __init__(self) -> None:
        self.select: AllSelects = None

    def to_view(self, timeout: float = None) -> ui.View:
        if self.select:
            return ui.View(timeout=timeout).add_item(self.select)
        return ui.View(timeout=timeout)
        
    def _select_handler(self, select_type: AllSelects, select_options: dict[str, typing.Any], view: ui.View = None) -> AllSelects | ui.View:
        try:
            self.select: AllSelects = select_type(**select_options)
            if view and self.select:
                return view.add_item(self.select)
            return self.select

        except Exception as error:
            print(f"Internal error in SelectMenus: {type(error).__name__}: {error}")

    def channel_select(self, view: ui.View = None, **select_options) -> ChannelSelect | ui.View:
        return self._select_handler(ChannelSelect, select_options, view)
    
    def role_select(self, view: ui.View = None, **select_options) -> RoleSelect | ui.View:
        return self._select_handler(RoleSelect, select_options, view)
    
    def user_select(self, view: ui.View = None, **select_options) -> UserSelect | ui.View:
        return self._select_handler(UserSelect, select_options, view)
    
    def custom_select(self, view: ui.View = None, **select_options) -> Select | ui.View:
        return self._select_handler(Select, select_options, view)
    
    def mentionable_select(self, view: ui.View = None, **select_options) -> MentionableSelect | ui.View:
        return self._select_handler(MentionableSelect, select_options, view)