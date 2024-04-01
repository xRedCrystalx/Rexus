import sys, discord, typing, ast
sys.dont_write_bytecode = True
import src.connector as con

from discord.ui import RoleSelect, ChannelSelect, UserSelect, Select, MentionableSelect, Button

if typing.TYPE_CHECKING:
    from .base_handler import AdvancedPaginator

class Configuration:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared

        self.FALLBACK: dict = dict(title="Configuration Wizard 🪄", description="This plugin does not have any configurations! ✨", timestamp=self.shared._datetime(), color=discord.Colour.dark_embed())
        self.MAIN_SCREEN: dict = dict(title="Configuration Wizard 🪄", description="Choose an option from the buttons below and I will help you with the request! ✨\n\n**PS:**\n Use `Enabled/Disabled` button for fast plugin switch! 🌠", timestamp=self.shared._datetime(), color=discord.Colour.dark_embed())
        self.EMBED: dict = dict(title="Configuration Wizard 🪄", timestamp=self.shared._datetime(), color=discord.Colour.dark_embed())

        self.config: dict[str, dict[str, str | list] | list | str] = {
            "alt" : {
                "embed": self.MAIN_SCREEN,
                "view": [{"name": "btn_switch"}, {"name": "btn_edit"}, {"name": "return"}],
                "btn_edit": {
                    "embed": {**self.EMBED, "description": "Choose **one** plugin setting from the list to continue."},
                    "view": [{"name": "slc_select", "kwargs" : {"options" : [discord.SelectOption(label="Status", value="status", description="Enable/Disable plugin"), discord.SelectOption(label="Logging Channel", description="Set plugin's logging channel.", value="log_channel")]}}, {"name": "btn_back"}],
                    "status": {
                        "embed": {**self.EMBED, "description": "Description 2"},
                        "view": [{"name": "btn_enable"}, {"name": "btn_disable"}, {"name": "btn_back"}],
                        "btn_enable": {
                            "path": "alt.status",
                            "value": (True, None, "Final"),
                            "return": 2
                        },
                        "btn_disable": {
                            "path": "alt.status",
                            "value": (False, None, "Final"),
                            "return": 2
                        }
                    },
                    "log_channel": {
                        "embed": {**self.EMBED, "description": "Choose **one Text Channel** that will be used to log events"},
                        "view": [{"name": "slc_channel", "kwargs": {"channel_types": [discord.ChannelType.text]}}, {"name": "btn_back"}],
                        "slc_channel": {
                            "path": "alt.log_channel",
                            "value": ("SELF", None, "Final"),
                            "return": 2
                        }
                    }
                }
            },
            "imper" : {
                "embed": self.MAIN_SCREEN,
                "view": [{"name": "btn_switch"}, {"name": "btn_edit"}, {"name": "return"}],
                "btn_edit": {
                    "embed": {**self.EMBED, "description": "Choose **one** plugin setting from the list to continue."},
                    "view": [{"name": "slc_select", "kwargs" : {"options" : [discord.SelectOption(label="Status", value="status", description="Enable/Disable plugin"), discord.SelectOption(label="Logging Channel", description="Set plugin's logging channel.", value="log_channel")]}}, {"name": "btn_back"}],
                    "status": {
                        "embed": {**self.EMBED, "description": "Description 2"},
                        "view": [{"name": "btn_enable"}, {"name": "btn_disable"}, {"name": "btn_back"}],
                        "btn_enable": {
                            "path": "imper.status",
                            "value": (True, None, "Final"),
                            "return": 2
                        },
                        "btn_disable": {
                            "path": "imper.status",
                            "value": (False, None, "Final"),
                            "return": 2
                        }
                    },
                    "log_channel": {
                        "embed": {**self.EMBED, "description": "Choose **one Text Channel** that will be used to log events"},
                        "view": [{"name": "slc_channel", "kwargs": {"channel_types": [discord.ChannelType.text]}}, {"name": "btn_back"}],
                        "slc_channel": {
                            "path": "imper.log_channel",
                            "value": ("SELF", None, "Final"),
                            "return": 2
                        }
                    }
                }
            },
            "link" : {
                "view" : ["switch", "edit", "return"]
            },
            "ping" : {
                "view" : ["switch", "create", "edit", "remove", "return"]
            },
            "autodelete" : {
                "view" : ["switch", "create", "edit", "remove", "return"]
            },
            "autoslowmode" : {
                "view" : ["switch", "create", "edit", "remove", "return"]
            },
            "ai" : {
                "embed": self.MAIN_SCREEN,
                "view": [{"name": "btn_switch"}, {"name": "btn_edit"}, {"name": "return"}],
                "btn_edit": {
                    "embed": {**self.EMBED, "description": "Choose **one** plugin setting from the list to continue."},
                    "view": [{"name": "slc_select", "kwargs" : {"options" : [discord.SelectOption(label="Status", value="status", description="Enable/Disable plugin"), discord.SelectOption(label="Respond channels", description="Channels where the AI will respond in.", value="respond")]}}, {"name": "btn_back"}],
                    "status": {
                        "embed": {**self.EMBED, "description": "Description 2"},
                        "view": [{"name": "btn_enable"}, {"name": "btn_disable"}, {"name": "btn_back"}],
                        "btn_enable": {
                            "path": "ai.status",
                            "value": (True, None, "Final"),
                            "return": 2
                        },
                        "btn_disable": {
                            "path": "ai.status",
                            "value": (False, None, "Final"),
                            "return": 2
                        }
                    },
                    "respond": {
                        "embed": {**self.EMBED, "description": "Choose what do you want to do."},
                        "view": [{"name": "btn_add"}, {"name": "btn_remove"}, {"name": "btn_back"}],
                        "exec": ""
                    }
                }
            }
        }
        
        self.config_history: list[dict] = [self.config]
        self.current_config: dict = self.config

    def navigate(self, key: str = None) -> dict:
        if key:
            if cnf := self.config_history[-1].get(key):
                self.config_history.append(cnf)
                self.current_config = cnf
                return cnf
        else:
            self.config_history.pop()
            self.current_config = self.config_history[-1]
            return self.config_history[-1]

    def reset_navigation(self) -> None:
        self.config_history = [self.config]
        self.current_config = self.config
        self.config_value = []

    def add_footer(self, embed: discord.Embed, text: str = None) -> discord.Embed:
        if not text:
            return embed.set_footer(text=f"Configuration for {self.view.global_config.get(self.option)["name"]}")
        else:
            return embed.set_footer(text=text)

    def format_embed(self, kwargs: dict) -> discord.Embed:
        return self.add_footer(discord.Embed(**kwargs), "✅ Sucessfully applied configuration settings." if "Final" in self.config_value else None)

    def handle_view(self):
        try:
            discord_items: dict[str, tuple[typing.Callable, dict[str, typing.Any]]] = {
                "btn_create": (Button, dict(label="Create", custom_id="CONFIG:btn_create", style=discord.ButtonStyle.green)),
                "btn_edit": (Button, dict(label="Edit", custom_id="CONFIG:btn_edit", style=discord.ButtonStyle.gray)),
                "btn_remove": (Button, dict(label="Remove", custom_id="CONFIG:btn_remove", style=discord.ButtonStyle.red)),
                "btn_back": (Button, dict(label="Back", custom_id="CONFIG:btn_back", style=discord.ButtonStyle.red)),
                "btn_switch": (Button, dict(label="Enabled" if self.guild_db[self.option].get("status") else "Disabled", custom_id="CONFIG:btn_switch", style=discord.ButtonStyle.green if self.guild_db[self.option].get("status") else discord.ButtonStyle.red)),
                "btn_enable": (Button, dict(label="Enable", custom_id="CONFIG:btn_enable", style=discord.ButtonStyle.green)),
                "btn_disable": (Button, dict(label="Disable", custom_id="CONFIG:btn_disable", style=discord.ButtonStyle.red)),
                "btn_add": (Button, dict(label="Add", custom_id="CONFIG:btn_add", style=discord.ButtonStyle.green)),
                "btn_remove": (Button, dict(label="Remove", custom_id="CONFIG:btn_remove", style=discord.ButtonStyle.red)),

                "slc_role": (RoleSelect, dict(custom_id="CONFIG:slc_role")),
                "slc_channel": (ChannelSelect, dict(custom_id="CONFIG:slc_channel")),
                "slc_member": (UserSelect, dict(custom_id="CONFIG:slc_member")),
                "slc_mentionable": (MentionableSelect, dict(custom_id="CONFIG:slc_mentionable")),
                "slc_select": (Select, dict(custom_id="CONFIG:slc_select")),

                "return": (self.view.create_back_button, {"item": True})
            }
            self.view.clear_items()

            for item in self.current_config.get("view", ()):
                if object := discord_items.get(item["name"]):
                    if kwargs := item.get("kwargs"):
                        object[1].update(**kwargs)
                    self.view.add_item(object[0](**object[1]))
            return self.view

        except Exception as error:
            self.shared.logger.log(f"@Configuration.create_buttons > {type(error).__name__}: {error}", "ERROR")

    def handle_db(self, item_id: str, interaction: discord.Interaction) -> None:
        def save_to_database(path: str, value: typing.Any, func: str = None) -> None:
            if not path:
                raise ValueError("Path provided equals None | configurator.py")

            keys: list[str] = path.split(".")
            database: dict[str, str | dict[str, str | int] | int] = self.guild_db
            for key in keys[:-1]:
                if key in database:
                    database = database[key]
                else:
                    raise MemoryError(f"Failed to reach value specified: {path}")
            
            # datatypes
            if isinstance(database[keys[-1]], (list, dict)):
                if func:
                    try:
                        getattr(database[keys[-1]], func)(value)
                    except:
                        pass
                else:
                    raise AttributeError(f"Missing function type argument on {type(database[keys[-1]])} type. > Path: {path}")
            else:
                if isinstance(value, list):
                    database[keys[-1]] = value[0]
                else:
                    database[keys[-1]] = value

            self.shared.db.save_data(interaction.guild.id, self.guild_db)
            return
        
        def local_save():
            ...

        interaction_data: dict[str, str | list[str] | dict[str, typing.Any]] =  dict(interaction.data)

        if item_id.startswith("btn_"):
            self.config_value: tuple[typing.Any, str, str] = self.current_config.get("value")
            if "Final" in self.config_value:
                save_to_database(path=self.current_config.get("path"), value=self.config_value[0], func=self.config_value[1])
            else:
                local_save()

        elif item_id.startswith("slc_"):
            values: list[int | str] = [ast.literal_eval(value) for value in interaction_data.get("values")]
            self.config_value: tuple[typing.Any, str, str] = self.current_config.get("value")
            if "Final" in self.config_value:
                save_to_database(path=self.current_config.get("path"), value=values if self.config_value[0] == "SELF" else self.config_value[0], func=self.config_value[1])
            else:
                local_save()

    async def handle_first_screen(self, interaction: discord.Interaction) -> None:
        if self.navigate(self.option):
            await self.view.update_message(interaction, {"embed": self.add_footer(self.format_embed(self.MAIN_SCREEN)), "view": self.handle_view()})
            """
        for path_list in self.config.keys():
            if self.option in path_list:
                self.navigate(path_list)
                await self.view.update_message(interaction, {"embed": self.add_footer(self.format_embed(self.MAIN_SCREEN)), "view": self.handle_view()})
                break
"""
        else:
            await self.view.update_message(interaction, {"embed": self.add_footer(self.format_embed(self.FALLBACK)), "view": self.view.clear_items().create_back_button()})

    async def handle_interaction(self, custom_id: str, interaction: discord.Interaction, view) -> None:
        if not view:
            return
        
        if not (guild_db := self.shared.db.load_data(interaction.guild.id)):
            return

        self.view: AdvancedPaginator = view
        self.option: str = self.view.current_position
        self.guild_db: dict[str, str | dict[str, str | int] | int] = guild_db

        if custom_id.endswith(":START"):
            self.reset_navigation()
            await self.handle_first_screen(interaction)

        elif custom_id.endswith(":btn_switch"):
            self.guild_db[self.option]["status"] = not self.guild_db[self.option]["status"]
            self.shared.db.save_data(interaction.guild.id, self.guild_db)
            await self.handle_first_screen(interaction)

        else:
            # actual logic and resloving
            item_id: str = custom_id.split(":")[-1]

            if item_id == "btn_back":
                self.navigate(None)
            
            elif item_id == "slc_select":
                self.navigate(interaction.data.get("values")[0])

            elif self.navigate(item_id):
                if self.current_config.get("value"):
                    self.handle_db(item_id, interaction)
            else:
                raise NotImplementedError("Failed to navigate interaction in the config.")
            
            if not (self.current_config.get("embed") and self.current_config.get("view")):
                if repeat_return := self.current_config.get("return"):
                    for _ in range(repeat_return):
                        self.navigate(None)
                else:
                    raise NotImplementedError(f"Missing `return` value in {self.config_history[-1]} config.")

            # display logic
            if self.current_config.get("embed") and self.current_config.get("view"):
                await self.view.update_message(interaction, dict(embed=self.format_embed(self.current_config.get("embed")), view=self.handle_view()))
            else:
                raise NotImplementedError("Could not locate embed or view in the config.")
            
            self.config_value = []





"""
{
    "general": {
        "allowAdminEditing": false,
        "staffRole": null,
        "staffChannel": null,
        "adminChannel": null
    },
    "alt": {
        "status": true,
        "log_channel": 1015937645135790120
    },
    "imper": {
        "status": false,
        "log_channel": 1015937645135790120
    },
    "ai": {
        "status": true,
        "log_channel": 1015937645135790120,
        "talkChannels": [
            1032353612665466992,
            1037720138335662141,
            1043532394042503198
        ]
    },
    "automod": {
        "status": false,
        "log_channel": 1015937645135790120
    },
    "link": {
        "status": false,
        "log_channel": 1015937645135790120,
        "options": {
            "allowDiscordInvites": false,
            "allowSocialLinks": false,
            "allowNitroGifts": false
        }
    },
    "ping": {
        "status": false,
        "detectReplyPings": false,
        "bypassRole": null,
        "ignoredChannels": [],
        "rules": {
            "MemberProtection": {
                "role": 996861513409249373,
                "ping": false,
                "logChannel": 1015937645135790120,
                "log": true,
                "delete": false
            },
            "StaffProtection": {
                "role": 996878384867065967,
                "ping": false,
                "logChannel": 1015937645135790120,
                "log": true,
                "delete": false
            },
            "Bot": {
                "role": "Every bot",
                "ping": false,
                "log": true,
                "logChannel": 1015937645135790120,
                "delete": false
            }
        }
    },
    "autodelete": {
        "status": false,
        "log_channel": 1015937645135790120,
        "monitored": []
    },
    "autoslowmode": {
        "status": false,
        "log_channel": null,
        "monitored": {
            "1032353612665466992": 102
        }
    },
    "reaction": {
        "status": false,
        "log_channel": 1015937645135790120,
        "reactionBanRole": null
    },
    "QOFTD": {
        "status": false,
        "log_channel": 1032353612665466992
    },
    "cmd": {
        "allowed": true
    },
    "Plugins": {
        "AI": true,
        "Alt": false,
        "Impersonator": false,
        "Link": true,
        "Reaction": false,
        "AutoMod": false,
        "Ping": true,
        "AutoDelete": true,
        "LevelingSystem": false,
        "Responder": true,
        "AutoSlowmode": false,
        "FanArt": false,
        "ReactionFilter": true,
        "Achievements": false,
        "QOFTD": true
    },
    "Logging": {
        "Alt": null,
        "Impersonator": null,
        "Link": 1015937645135790120,
        "AutoSlowmode": null,
        "AutoDelete": 1015937645135790120,
        "LevelingSystem": null,
        "ReactionFilter": 1015937645135790120,
        "Achievements": null,
        "QOFTD": 1032353612665466992
    },
    "PingProtection": {
        "BypassRole": null,
        "IgnoreChannels": [],
        "DetectReplyPings": false,
        "MemberProtection": {
            "Role": null,
            "Ping": false,
            "Log": false,
            "Delete": false,
            "LogChannel": null
        },
        "StaffProtection": {
            "Role": null,
            "Ping": false,
            "Log": false,
            "Delete": false,
            "LogChannel": null
        },
        "YouTuberProtection": {
            "Role": null,
            "Ping": false,
            "Log": null,
            "Delete": false,
            "LogChannel": null
        },
        "Everyone/Here": {
            "Ping": false,
            "Log": false,
            "Delete": false,
            "LogChannel": null
        },
        "Bot": {
            "Ping": false,
            "Log": true,
            "Delete": true,
            "LogChannel": 1015937645135790120
        }
    },
    "ServerInfo": {
        "StaffRole": null,
        "StaffChannel": null,
        "LogChannel": null
    },
    "AutoSlowmode": [],
    "AutoMod": {},
    "AutoDelete": {
        "1015937738823970856": 5
    },
    "AutoResponder": {
        "-joinmm2": {
            "startsWith": true,
            "content": "**How do I play MM2 with Ant?**\n\n- When Ant is hosting a game of MM2, he'll post a join link in <#871141617170513950>. Click that link to join the game.\n- Try to be fast! The game fills up quickly!"
        }
    },
    "FanArt": [
        1037720138335662141
    ],
    "AI": 1095810937501532200,
    "ReactionFilter": {
        "role": 1203444406108295258
    },
    "LevelingSystem": {
        "config": {
            "levels": {
                "message": false,
                "voice": false,
                "reaction": false,
                "giveaway": false
            },
            "notifications": {
                "dm": {
                    "send": false,
                    "ping": false,
                    "message": "Congrats {member}, you just advanced to {type} level {num}!"
                },
                "guild": {
                    "send": false,
                    "ping": false,
                    "message": "Congrats {member}, you just advanced to {type} level {num}!"
                }
            },
            "rewards": {
                "message": {},
                "voice": {},
                "reaction": {},
                "giveaway": {}
            },
            "achievements": {},
            "switch": ""
        },
        "members": {}
    }
}
"""