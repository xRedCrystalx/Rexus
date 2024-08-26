import sys, discord
sys.dont_write_bytecode = True
from typing import Self
from discord import Embed

from .emojis import CustomEmoji as CEmoji

from xRedUtils.dates import get_datetime, timestamp
from xRedUtils.type_hints import SIMPLE_ANY


class EmbedGenerator(Embed):
    def __init__(self, title: str = None, description: str = None) -> None:
        super().__init__(title=title, description=description, timestamp=get_datetime(), colour=discord.Colour.dark_embed())

    # superclass methods:
    # .set_author, .set_thumbnail, .set_image, .set_footer, .set_field_at, .add_field, .insert_field_at
    # .remove_field, clear_fields, .remove_footer, .remove_author
    # .copy, .to_dict

    # missing methods
    def set_color(self, color: str | int | discord.Colour) -> Self:
        self.colour = color
        return self

    def remove_color(self) -> Self:
        self.color = None
        return self

    def remove_image(self) -> Self:
        try:
            del self._image
        except AttributeError:
            pass
    
    def remove_thumbnail(self) -> Self:
        try:
            del self._thumbnail
        except AttributeError:
            pass

    # verify checks

    # custom fields
    def add_member_field(self, account: discord.Member | discord.User, inline: bool = True) -> Self:
        if isinstance(account, discord.Member | discord.User):
            self.add_field(
                name=f"` {account.__class__.__name__.capitalize()} `", 
                value=f"{CEmoji.PROFILE}┇{account.mention}\n{CEmoji.GLOBAL}┇{account.name}\n{CEmoji.ID}┇{account.id}", 
                inline=inline
            )
        return self
    
    def add_guild_channel_field(self, channel: discord.abc.GuildChannel, inline: bool = True) -> Self:
        if isinstance(channel, discord.abc.GuildChannel):
            self.add_field(
                name=f"` Channel `",
                # category is optional due to possibility of channel not being under a category
                value=f"{CEmoji.TEXT_C}┇{channel.mention}{f"\n**Category**┇{channel.category.mention}" if channel.category else ""}\n**Type**┇{channel.type.name.replace("_", " ").title()}\n{CEmoji.ID}┇{channel.id}",
                inline=inline
            )
        return self

    def add_role_field(self, role: discord.Role, inline: bool = True) -> Self:
        if isinstance(role, discord.Role):
            self.add_field(
                name="` Role `",
                value=f"{CEmoji.ROLE}┇{role.mention}\n**Position**┇`{role.position}`\n**Creation**┇<t:{timestamp(role.created_at)}:f>\n{CEmoji.ID}┇{role.id}\n{CEmoji.ART}┇`{str(role.colour).upper()}`", # color should return HEX
                inline=inline
            )
        return self

    def add_category_field(self, category: discord.CategoryChannel, inline: bool = True) -> Self:
        if isinstance(category, discord.CategoryChannel):
            self.add_field(
                name="` Category `",
                value=f"**Name**┇{category.mention}\n**Creation**┇<t:{timestamp(category.created_at)}:f>\n{CEmoji.ID}┇{category.id}",
                inline=inline
            )
        return self

    def add_message_location_field(self, message: discord.Message, inline: bool = True) -> Self:
        if isinstance(message, discord.Message):
            self.add_field(
                name="` Location `",
                value=f"{CEmoji.MESSAGE}┇{message.jump_url}\n{CEmoji.TEXT_C}┇{message.channel.mention}\n{CEmoji.ID}┇{message.channel.id}",
                inline=inline
            )
        return self

    def add_invite_link_field(self, invite: discord.Invite, inline: bool = True) -> Self:
        if isinstance(invite, discord.Invite):
            self.add_field(
                name="` Invite link `",
                value=f"{CEmoji.ID}┇`{invite.code}`\n**Expiration**┇<t:{timestamp(invite.expires_at) if invite.expires_at else "`Infinite`"}:R>\n[` Invite Link `]({invite.url})",
                inline=inline
            )
        return self

    """def add_webhook_field(self, webhook: discord.Webhook, inline: bool = True) -> Self:
        if isinstance(webhook, discord.Webhook):
            self.add_field(
                name="` Webhook `",
                value=f"{CEmoji.MSG_ID}┇{message.id}\n{CEmoji.TEXT_C}┇{message.channel.mention}\n{CEmoji.ID}┇{message.channel.id}",
                inline=inline
            )
        return self"""

    def add_thread_field(self, thread: discord.Thread, inline: bool = True) -> Self:
        if isinstance(thread, discord.Thread):
            self.add_field(
                name="` Location `",
                value=f"**Name**┇{thread.name}\n{CEmoji.ID}┇`{thread.id}`{f"\n{CEmoji.TEXT_C}┇{thread.parent.mention}" if thread.parent else ""}{f"\n{CEmoji.PING}┇{thread.owner.mention}" if thread.owner else ""}",
                inline=inline
            )
        return self

    """def add_integration_field(self, integration: discord.Integration, inline: bool = True) -> Self:
        if isinstance(integration, discord.Integration):
            self.add_field(
                name="` Location `",
                value=f"**Name**┇{thread.name}\n{CEmoji.ID}┇`{thread.id}`{f"\n{CEmoji.TEXT_C}┇{thread.parent.mention}" if thread.parent else ""}{f"\n{CEmoji.PING}┇{thread.owner.mention}" if thread.owner else ""}",
                inline=inline
            )
        integration.type
        return self"""

    def add_emoji_or_sticker_field(self, eors: discord.Emoji | discord.Sticker, inline: bool = True) -> Self:
        if isinstance(eors, discord.Emoji | discord.Sticker):
            self.add_field(
                name=f"` {eors.__class__.__name__.capitalize()} `",
                value=f"**Name**┇{eors.name}\n{CEmoji.ID}┇`{eors.id}`",
                inline=inline
            )
            self.set_image(url=eors.url)
        return self

class Embeds:
    GENERAL_NO_PERMISSIONS: EmbedGenerator = EmbedGenerator(title="No permissions", description="You are not allowed to do that!").set_color(0xFF0000)
    COMMAND_NO_PERMISSIONS: EmbedGenerator = EmbedGenerator(title="No permissions", description="You are not allowed to do run this command!").set_color(0xFF0000)

    @staticmethod
    def new_error_embed(error_id: str) -> EmbedGenerator:
        """|sync|"""
        return EmbedGenerator(title="Error", description=f"An error has occured. Please report this to the developer.\n**Error code:** `{error_id}`")