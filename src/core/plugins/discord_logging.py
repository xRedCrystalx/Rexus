import discord, sys, asyncio
sys.dont_write_bytecode = True
from src.connector import shared
from discord import Webhook, AuditLogEntry
from discord.ext import commands

from ..helpers.embeds import EmbedGenerator
from ..helpers.emojis import EmojiImage as EI, CustomEmoji as CE
from ..helpers.discord_formats import *
from ..helpers.errors import report_error
from ..helpers.permissions import check_ids, check_channel_type

from xRedUtilsAsync.type_hints import SIMPLE_ANY
from xRedUtilsAsync.iterables import to_iterable, compare_iterables, count_occurrences
from xRedUtilsAsync.strings import pluralize, singularize, string_split
from xRedUtilsAsync.dates import get_datetime, timestamp

"""
CREATE/DELETE Embed
    title: [action] [target]
    field: n: [target] v: [info generation?]
    footer: img: member_pfp, member_name, timestamp
    color:  set_embed_color()

"""

class LogEmbedGeneration:
    def __init__(self) -> None:
        self._special_titles: dict[str, str] = {
            "on_member_ban": "Member banned"
        }

    # general functions
    def embed_color(self, action: str) -> int:
        if action in ("create", "add"):
            return 0x00FF00 # green
        elif action in ("edit", "update"):
            return 0xFFFF00 # yellow
        elif action in ("delete", "remove"):
            return 0xFF0000 # red
        
        return discord.Colour.dark_embed()
    
    async def field_overflow_handler(self, embed: EmbedGenerator, name: str, value: str) -> EmbedGenerator:
        for chunk in await string_split(value, 1000, "smart", _sep="\n"):
            embed.add_field(name=name, value=chunk, inline=False)

        return embed

    def humanize_event_name(self, event_name: str) -> str:
        if (special_title := self._special_titles.get(event_name)):
            return special_title

        if "raw" in event_name:
            event_name = event_name.removeprefix("on_raw_")
        else:
            event_name = event_name.removeprefix("on_")

        event_name = event_name.replace("_", " ").capitalize()

        if event_name.endswith("e"):
            return event_name+"d"
        else:
            return event_name+"ed"

    # embed creators
    def update_generator(self) -> EmbedGenerator:
        ...

    def non_update_generator(self) -> EmbedGenerator:
        ...

    async def generate(self, event_name: str, action_category: str, information: dict[str, SIMPLE_ANY]) -> EmbedGenerator:
        embed: EmbedGenerator = EmbedGenerator(
            title=self.humanize_event_name(event_name)
        ).set_color(self.embed_color(action_category))
        
        

class DiscordLogger:
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.generator = LogEmbedGeneration()
        self.event_db: dict[int, dict[str, object]] = {} # target ID: event_data
        self.completed_events: list[int] = []
        self.bot: commands.AutoShardedBot = bot

        self._single_events: list[str] = [
            "on_raw_poll_vote_add", 
            "on_raw_poll_vote_remove", 
            "on_raw_message_edit", 
            "on_raw_reaction_add", 
            "on_raw_reaction_remove",
            "on_raw_reaction_clear",
            "on_raw_reaction_clear_emoji",
            "on_scheduled_event_user_add",
            "on_scheduled_event_user_remove",
            "on_thread_remove",
            "on_thread_member_join",
            "on_raw_thread_member_remove",
            "on_voice_state_update"
        ]
        self._resolver_specials: dict[str, str] = {
            # payloads
            "on_raw_app_command_permissions_update": "target_id",
            "on_raw_integration_delete": "integration_id",
            "on_raw_message_delete": "message_id",
            "on_raw_bulk_message_delete": "channel_id",
            "on_raw_thread_update": "thread_id",
            "on_raw_thread_delete": "thread_id",

            # correct objects for multi-object events
            "on_guild_channel_pins_update": "channel",
            "on_guild_emojis_update": "guild",
            "on_guild_stickers_update": "guild",
            "on_member_ban": "user",
            "on_member_unban": "user",
        }

    def _resolve_user(self, obj: object) -> None | discord.User | discord.Member:
        return getattr(obj, "member", None) or getattr(obj, "user", None) or getattr(obj, "author", None)

    async def _events_to_data(self, *events) -> dict[str, SIMPLE_ANY]:
        # events can be either 0, 1 or 2

        information: dict[str, SIMPLE_ANY] = {}
        
        # empty list for whatever reason (num 0 = False)
        if not (event_num := len(events)):
            return

        elif event_num == 1:
            event: dict[str, object | str] = events[0]

            information["WEBHOOK"] = event.get("WEBHOOK")
            information["action"] = event.get("DISCORD_EVENT")

            # only entry
            if (entry := event.get("entry")) and isinstance(entry, AuditLogEntry):
                return information | {
                    "action": entry.category.name, # resolver needed
                    "target": entry.target,
                    "moderator": entry.user if entry.user else self.bot.get_user(entry.user_id) if entry.user_id else None,
                    "changes": entry.changes,
                    "events": {
                        "entry": entry
                    }
                }

            # only normal event
            elif event_keys := [key for key in event.keys() if key not in ["WEBHOOK", "DISCORD_EVENT"]]:
                # update event
                if (before := event.get("before")) and (after := event.get("after")):
                    return information | {
                        "target": after,
                        "moderator": self._resolve_user(after),
                        "events": {
                            key: event.get(key) for key in event_keys
                        }
                    }

                # other single events
                else:
                    return information | {
                        
                    }

        elif event_num == 2:
            ...

        # more than 2 events, logging the case
        else:
            shared.logger.log("TESTING", f"@DiscordLogger._events_to_data > Got {event_num} events.\n{"\n".join([f"{event}" for event in events])}")

        return information

    async def _resolve_target(self, event_name: str, event_data: dict[str, object]) -> int:
        # entry - normally alone in the event data, returns targed.id
        if (entry := event_data.get("entry")) and isinstance(entry, AuditLogEntry):
            target_id: int = entry.target.id
            shared.logger.log("TESTING", f"@DiscordLogger._resolve_target > Resolved audit log entry ID: {target_id}")

        # raw payloads - they don't have .id, but .xyz_id - defined under self._resolver_specials
        elif (attr := self._resolver_specials.get(event_name)) and (payload := event_data.get("payload")):
            target_id: int = getattr(payload, attr, None)
            shared.logger.log("TESTING", f"@DiscordLogger._resolve_target > Resolved payload ID: {target_id}")

        # if either before or after, this is "update" event and both objects have same ID
        elif (obj := event_data.get("after") or event_data.get("before")):
            target_id: int = getattr(obj, "id", None)
            shared.logger.log("TESTING", f"@DiscordLogger._resolve_target > Resolved update ID: {target_id}")

        # multiple argument events - defined under self._resolver_specials aswell
        elif (key := self._resolver_specials.get(event_name)):
            target_id: int = getattr(event_data.get(key), "id", None)
            shared.logger.log("TESTING", f"@DiscordLogger._resolve_target > Resolved multiple argument event ID: {target_id}")
        
        # single argument events
        elif len(keys := tuple(event_data.keys())) == 1:
            target_id = getattr(event_data.get(keys[0]), "id", None)
            shared.logger.log("TESTING", f"@DiscordLogger._resolve_target > Resolved single argument event ID: {target_id} - {keys[0]}")

        else:
            target_id = None
            shared.logger.log("TESTING", f"@DiscordLogger._resolve_target > Unresolved on event `{event_name}` and data: {event_data}")

        return target_id

    async def _lifetime(self, event_id: int) -> None:
        """Event lifetime - 2.5s (preventing memory leak)"""
        await asyncio.sleep(2.5)

        if event_id in self.completed_events:
            self.completed_events.remove(event_id)
        else:
            await self.log_event(event_id)

        self.event_db.pop(event_id)

    async def log_event(self, event_id: int, event_data: dict[str, SIMPLE_ANY] | None = None) -> None:
        self.completed_events.append(event_id)
        
        # Double event, normally log entry & normal event
        if event_id and event_data:
            information: dict[str, SIMPLE_ANY] = await self._events_to_data(event_data, self.event_db.get(event_id))

        # single event, normally non-entry event/non-guild logged
        elif not event_id and event_data:
            information: dict[str, SIMPLE_ANY] = await self._events_to_data(event_data)

        # expired event, expected either log entry or normal event, but not recieved - API/network errors
        elif event_id and not event_data:
            information: dict[str, SIMPLE_ANY] = await self._events_to_data(self.event_db.get(event_id))
        else:
            return
        
        shared.logger.log("TESTING", f"Resolved information of {event_id}:\n{"\n".join([f"{key}: {value}" for key, value in information.items()])}")

        # if events are resolved, embed gets created
        if not information:
            return

        log_embed: EmbedGenerator = None #await self.generator.generate()
        
        # if no embed or missing webhook, ignore
        if not (log_embed or (webhook_url := information.get("WEBHOOK"))):
            return
        
        # send log message
        if webhook_object := Webhook.from_url(webhook_url, session=shared.session):
            await webhook_object.send(embed=log_embed)

    async def process_event(self, guild_db: dict[str, SIMPLE_ANY], event_name: str, event_data: dict[str, object], **OVERFLOW) -> None:
        shared.logger.log("TESTING", f"@DiscordLogger.process_event > Recieved {event_name} event")

        #if not guild_db.get("status") or not guild_db.get(event_name, {}).get("status"):
        #    return
        
        # couldn't resolve target id
        if not (target_id := await self._resolve_target(event_name, event_data)):
            return
        
        full_event: dict[str, SIMPLE_ANY] = event_data | {"DISCORD_EVENT": event_name, "WEBHOOK": None} #guild_db.get(event_name, {}).get("webhook")

        # if either entry or normal event is already in local DB, sending a report
        if self.event_db.get(target_id):
            shared.logger.log("TESTING", f"@DiscordLogger.process_event > Double event - sending to _events_to_data handler.")
            await self.log_event(target_id, full_event)

        # if single event, run it
        elif event_name in self._single_events:
            shared.logger.log("TESTING", f"@DiscordLogger.process_event > Single event - sending to _events_to_data handler.")
            await self.log_event(None, full_event)

        else:
            # save to local DB and start lifetime cycle
            self.event_db[target_id] = full_event
            shared.loop.create_task(self._lifetime(target_id))
            shared.logger.log("TESTING", f"@DiscordLogger.process_event > Saved event to DB and started lifetime cycle.")

async def setup(bot: commands.AutoShardedBot) -> None:
    await shared.module_manager.load(dclogger := DiscordLogger(bot),
        config={
            dclogger.process_event: [
                "on_audit_log_entry_create", "on_guild_update",
                "on_automod_rule_create", "on_automod_rule_delete", "on_automod_rule_update",
                "on_guild_channel_create", "on_guild_channel_delete", "on_guild_channel_update", "on_guild_channel_pins_update",
                "on_guild_emojis_update", "on_guild_stickers_update",
                "on_invite_create", "on_invite_delete",
                "on_guild_role_create", "on_guild_role_delete", "on_guild_role_update",
                "on_member_join", "on_raw_member_remove", "on_member_update", "on_member_ban", "on_member_unban",
                "on_integration_create", "on_integration_update", "on_raw_integration_delete", "on_webhooks_update",
                "on_raw_message_edit", "on_raw_message_delete", "on_raw_bulk_message_delete",
                "on_scheduled_event_create", "on_scheduled_event_delete", "on_scheduled_event_update",
                "on_stage_instance_create", "on_stage_instance_delete", "on_stage_instance_update",
                "on_thread_create", "on_raw_thread_update", "on_raw_thread_delete"
            ]
        }
    )

# TODO: emebed generation, _events_to_data resolver


# handle whole logic of embed generation
# handle enabled/disabled loggers
# deal with audit logs
# deal with member and user
# run embed generation

"""
on_audit_log_entry_create > AuditLogEntry (https://discordpy.readthedocs.io/en/stable/api.html?#discord.AuditLogEntry)

AuditLogEntry:
- id: Entery ID
- target: Target of the entry (User, Guild, Channel, Role, etc.)
- action: AuditLogAction (.name)                      (https://discordpy.readthedocs.io/en/stable/api.html#discord.AuditLogAction)
[
    'guild_update',
    .'channel_create', 'channel_update', 'channel_delete', 
    'overwrite_create', 'overwrite_update', 'overwrite_delete',
    'kick', 'member_prune', 'ban', 'unban', 
    .'member_update', 'member_role_update', 'member_move', 'member_disconnect', 'bot_add',
    .'role_create', 'role_update', 'role_delete', 
    .'invite_create', 'invite_update', 'invite_delete', 
    .'webhook_create', 'webhook_update','webhook_delete', 
    .'emoji_create', 'emoji_update', 'emoji_delete', 
    'message_delete', 'message_bulk_delete', 'message_pin', 'message_unpin', 
    .'integration_create', 'integration_update', 'integration_delete', 
    'stage_instance_create', 'stage_instance_update', 'stage_instance_delete', 
    .'sticker_create', 'sticker_update', 'sticker_delete', 
    'scheduled_event_create', 'scheduled_event_update', 'scheduled_event_delete', 
    .'thread_create', 'thread_update', 'thread_delete', 
    'app_command_permission_update', 
    'automod_rule_create', 'automod_rule_update', 'automod_rule_delete', 'automod_block_message', 'automod_flag_message', 'automod_timeout_member', 
    'creator_monetization_request_created', 'creator_monetization_terms_accepted'
]

- category: AuditLogActionCategory (.name)            (https://discordpy.readthedocs.io/en/stable/api.html#discord.AuditLogActionCategory)

- changes: AuditLogChanges (no clue)
- before, after: AuditLogDiff 


    def event_to_data(self, event: object) -> dict[str, SIMPLE_ANY]:
        ...

    def entry_to_data(self, entry: AuditLogEntry | None) -> dict[str, SIMPLE_ANY] | None:
        if isinstance(entry, AuditLogEntry):
            return {
                "action": entry.action.name,
                "target": entry.target,
                "user": entry.user if entry.user else self.bot.get_user(entry.user_id) if entry.user_id else None,
                "timestamp": entry.created_at,
                "action_category": entry.category.name,
                "changes": entry.changes,
                "entry": entry
            }
        return None

    def _find_entry(self, event: dict[str, SIMPLE_ANY]) -> AuditLogEntry | None:
        return entry if (entry := event.get("entry")) and isinstance(entry, AuditLogEntry) else None


"""
