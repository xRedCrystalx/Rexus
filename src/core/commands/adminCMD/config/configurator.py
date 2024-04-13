import sys, discord, typing, ast
sys.dont_write_bytecode = True
import src.connector as con

from discord.ui import RoleSelect, ChannelSelect, UserSelect, Select, MentionableSelect, Button

if typing.TYPE_CHECKING:
    from .base_handler import AdvancedPaginator

"""
embed = dict[str, str]
view = list[dict[discord_items] | str[discord_items]]
db = list[str, Any, str | None, str] -> [0]: path, [1]: value > "SELF:{int|*}", [2]: func, [3]: type


local_db -> FULL DICT REQUIRED AT THE START
"""


class Configurator:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared

        self.FALLBACK: dict = dict(title="Configuration Wizard 🪄", description="This plugin does not have any configurations! ✨", color=discord.Colour.dark_embed())
        self.MAIN_SCREEN: dict = dict(title="Configuration Wizard 🪄", description="Choose an option from the buttons below and I will help you with the request! ✨\n\n**PS:**\n Use `Enabled/Disabled` button for fast plugin switch! 🌠", color=discord.Colour.dark_embed())

        self.config: dict[str, dict[str, str | list] | list | str] = {
            # not defined: commmands
            "general": {
                "embed": self.MAIN_SCREEN,
                "view": ["btn_switch", "btn_edit", "return"],
                "btn_edit": {
                    "embed": {"description": "Choose plugin setting from the list to continue."},
                    "view": [{"name": "slc_select", "kwargs" : {"options" : [
                        discord.SelectOption(label="Status", value="status", description="Enable/Disable bot"), 
                        discord.SelectOption(label="Admin Editing", value="allow_admin_editing", description="Allow/Disallow server admins to edit NoPing's configuration."),
                        discord.SelectOption(label="Staff/Mod role", value="staff_role", description="Set Mod/Staff's role, this is REQUIRED."),
                        discord.SelectOption(label="Staff/Mod chat", value="staff_chat", description="Set Mod/Staff's channel, this is REQUIRED."),
                        discord.SelectOption(label="Admin role", value="admin_role", description="Set Admin's role, this is REQUIRED."),
                        discord.SelectOption(label="Admin chat", value="admin_chat", description="Set Admin's channel, this is REQUIRED.")],
                        "placeholder": "Choose selection (you might need to scroll)"}}, "btn_back"],
                    "status": {
                        "embed": {"description": "Click on the buttons below to `Enable/Disable` **Bot!**\n**Current:** {status:boolean_format?option='switch'&discord_format}"},
                        "view": ["btn_enable", "btn_disable", "btn_back"],
                        "btn_enable": {
                            "db": ["general.status", True, None],
                            "return": 2
                        },
                        "btn_disable": {
                            "db": ["general.status", False, None],
                            "return": 2
                        }
                    },
                    "allow_admin_editing": {
                        "embed": {"description": "Click on the buttons below to `Allow/Disallow` **Admin Editing**\n**Current:** {allowAdminEditing:boolean_format?option='y/n'&discord_format}"},
                        "view": ["btn_enable", "btn_disable", "btn_back"],
                        "btn_enable": {
                            "db": ["general.allowAdminEditing", True, None],
                            "return": 2
                        },
                        "btn_disable": {
                            "db": ["general.allowAdminEditing", False, None],
                            "return": 2
                        }
                    },
                    "staff_role": {
                        "embed": {"description": "Choose **Role** that will be used as **Staff/Mod Role**.\n**Current:** {staffRole:id_format?option='role'}"},
                        "view": ["slc_role", "btn_back"],
                        "slc_role": {
                            "db": ["general.staffRole", "SELF:1", None],
                            "return": 2
                        }
                    },
                    "staff_chat": {
                        "embed": {"description": "Choose **Text Channel** that will be used as **Staff/Mod Channel**.\n**Current:** {staffChannel:id_format?option='channel'}"},
                        "view": [{"name": "slc_channel", "kwargs": {"channel_types": [discord.ChannelType.text]}}, "btn_back"],
                        "slc_channel": {
                            "db": ["general.staffChannel", "SELF:1", None],
                            "return": 2
                        }
                    },
                    "admin_role": {
                        "embed": {"description": "Choose **Role** that will be used as **Admin Role**.\n**Current:** {adminRole:id_format?option='role'}"},
                        "view": ["slc_role", "btn_back"],
                        "slc_role": {
                            "db": ["general.adminRole", "SELF:1", None],
                            "return": 2
                        }
                    },
                    "admin_chat": {
                        "embed": {"description": "Choose **Text Channel** that will be used as **Admin Channel**.\n**Current:** {adminChannel:id_format?option='channel'}"},
                        "view": [{"name": "slc_channel", "kwargs": {"channel_types": [discord.ChannelType.text]}}, "btn_back"],
                        "slc_channel": {
                            "db": ["general.adminChannel", "SELF:1", None],
                            "return": 2
                        }
                    }
                },
            },
            "alt" : {
                "embed": self.MAIN_SCREEN,
                "view": ["btn_switch", "btn_edit", "return"],
                "btn_edit": {
                    "embed": {"description": "Choose plugin setting from the list to continue."},
                    "view": [{"name": "slc_select", "kwargs" : {"options" : [
                        discord.SelectOption(label="Status", value="status", description="Enable/Disable plugin"), 
                        discord.SelectOption(label="Logging Channel", description="Set plugin's logging channel.", value="log_channel")]}}, "btn_back"],
                    "status": {
                        "embed": {"description": "Click on the buttons below to `Enable/Disable` **Alt detection!**\n**Current:** {status:boolean_format?option='switch'&discord_format}"},
                        "view": ["btn_enable", "btn_disable", "btn_back"],
                        "btn_enable": {
                            "db": ["alt.status", True, None],
                            "return": 2
                        },
                        "btn_disable": {
                            "db": ["alt.status", False, None],
                            "return": 2
                        }
                    },
                    "log_channel": {
                        "embed": {"description": "Choose **Text Channel** that will be used to log events.\n**Current:** {log_channel:id_format?option='channel'}"},
                        "view": [{"name": "slc_channel", "kwargs": {"channel_types": [discord.ChannelType.text]}}, "btn_back"],
                        "slc_channel": {
                            "db": ["alt.log_channel", "SELF:1", None],
                            "return": 2
                        }
                    }
                }
            },
            "imper" : {
                "embed": self.MAIN_SCREEN,
                "view": ["btn_switch", "btn_edit", "return"],
                "btn_edit": {
                    "embed": {"description": "Choose plugin setting from the list to continue."},
                    "view": [{"name": "slc_select", "kwargs" : {"options" : [
                        discord.SelectOption(label="Status", value="status", description="Enable/Disable plugin"), 
                        discord.SelectOption(label="Logging Channel", value="log_channel", description="Set plugin's logging channel.")]}}, "btn_back"],
                    "status": {
                        "embed": {"description": "Click on the buttons below to `Enable/Disable` **Impersonator detection!**\n**Current:** {status:boolean_format?option='switch'&discord_format}"},
                        "view": ["btn_enable", "btn_disable", "btn_back"],
                        "btn_enable": {
                            "db": ["imper.status", True, None],
                            "return": 2
                        },
                        "btn_disable": {
                            "db": ["imper.status", False, None],
                            "return": 2
                        }
                    },
                    "log_channel": {
                        "embed": {"description": "Choose **Text Channel** that will be used to log events.\n**Current:** {log_channel:id_format?option='channel'}"},
                        "view": [{"name": "slc_channel", "kwargs": {"channel_types": [discord.ChannelType.text]}}, "btn_back"],
                        "slc_channel": {
                            "db": ("imper.log_channel", "SELF:1", None),
                            "return": 2
                        }
                    }
                }
            },
            "ai" : {
                "embed": self.MAIN_SCREEN,
                "view": ["btn_switch", "btn_edit", "return"],
                "btn_edit": {
                    "embed": {"description": "Choose plugin setting from the list to continue."},
                    "view": [{"name": "slc_select", "kwargs": {"options" : [
                        discord.SelectOption(label="Status", value="status", description="Enable/Disable plugin"), 
                        discord.SelectOption(label="Respond channels", value="respond", description="Channels where the AI will respond in.")]}}, "btn_back"],
                    "status": {
                        "embed": {"description": "Click on the buttons below to `Enable/Disable` **AI!**\n**Current:** {status:boolean_format?option='switch'&discord_format}"},
                        "view": ["btn_enable", "btn_disable", "btn_back"],
                        "btn_enable": {
                            "db": ["ai.status", True, None],
                            "return": 2
                        },
                        "btn_disable": {
                            "db": ["ai.status", False, None],
                            "return": 2
                        }
                    },
                    "respond": {
                        "embed": {"description": "Choose action setting from the buttons."},
                        "view": ["btn_add", "btn_remove", "btn_back"],
                        "btn_add": {
                            "embed": {"description": "Choose **Text Channel** that you want to add to the list.\n**Current:**\n{talkChannels:id_format?option='channel'&list_format}"},
                            "view":  [{"name": "slc_channel", "kwargs": {"channel_types": [discord.ChannelType.text]}}, "btn_back"],
                            "slc_channel": {
                                "db": ["ai.talkChannels", "SELF:1", "append"],
                                "return": 2
                            }
                        },
                        "btn_remove": {
                            "embed": {"description": "Choose **Text Channel** that you want to remove from the list.\n**Current:**\n{talkChannels:id_format?option='channel'&list_format}"},
                            "view":  [{"name": "slc_channel", "kwargs": {"channel_types": [discord.ChannelType.text]}}, "btn_back"],
                            "slc_channel": {
                                "db": ["ai.talkChannels", "SELF:1", "remove"],
                                "return": 2
                            }
                        }
                    }
                }
            },    
            "link" : {
                "embed": self.MAIN_SCREEN,
                "view": ["btn_switch", "btn_edit", "return"],
                "btn_edit": {
                    "embed": {"description": "Choose plugin setting from the list to continue."},
                    "view": [{"name": "slc_select", "kwargs": {"options" : [
                        discord.SelectOption(label="Status", value="status", description="Enable/Disable plugin"), 
                        discord.SelectOption(label="Logging Channel", value="log_channel", description="Set plugin's logging channel."), 
                        discord.SelectOption(label="Allow Discord Invites", value="dc_invites", description="Allow/Disallow discord invites."), 
                        discord.SelectOption(label="Allow Discord Gifs", value="dc_gifts", description="Allow/Disallow discord gifting."), 
                        discord.SelectOption(label="Allow Social Media Links", value="socials", description="Allow/Disallow Youtube, Twitch, X etc. links")]}}, "btn_back"],
                    "status": {
                        "embed": {"description": "Click on the buttons below to `Enable/Disable` **Link Protection!**\n**Current:** {status:boolean_format?option='switch'&discord_format}"},
                        "view": ["btn_enable", "btn_disable", "btn_back"],
                        "btn_enable": {
                            "db": ["link.status", True, None],
                            "return": 2
                        },
                        "btn_disable": {
                            "db": ["link.status", False, None],
                            "return": 2
                        }
                    },
                    "log_channel": {
                        "embed": {"description": "Choose **Text Channel** that will be used to log events.\n**Current:** {log_channel:id_format?option='channel'}"},
                        "view": [{"name": "slc_channel", "kwargs": {"channel_types": [discord.ChannelType.text]}}, "btn_back"],
                        "slc_channel": {
                            "db": ("link.log_channel", "SELF:1", None),
                            "return": 2
                        }
                    },
                    "dc_invites": {
                        "embed": {"description": "Click on the buttons below to `Allow/Disallow` **Discord Invites**\n**Current:** {options[allowDiscordInvites]:boolean_format?option='switch'&discord_format}"},
                        "view": ["btn_enable", "btn_disable", "btn_back"],
                        "btn_enable": {
                            "db": ["link.options.allowDiscordInvites", True, None],
                            "return": 2
                        },
                        "btn_disable": {
                            "db": ["link.options.allowDiscordInvites", False, None],
                            "return": 2
                        }
                    },
                    "dc_gifts": {
                        "embed": {"description": "Click on the buttons below to `Allow/Disallow` **Discord Gifts**\n**Current:** {options[allowNitroGifts]:boolean_format?option='switch'&discord_format}"},
                        "view": ["btn_enable", "btn_disable", "btn_back"],
                        "btn_enable": {
                            "db": ["link.options.allowNitroGifts", True, None],
                            "return": 2
                        },
                        "btn_disable": {
                            "db": ["link.options.allowNitroGifts", False, None],
                            "return": 2
                        }
                    },
                    "socials": {
                        "embed": {"description": "Click on the buttons below to `Allow/Disallow` **Social Accounts**\n**Current:** {options[allowSocialLinks]:boolean_format?option='switch'&discord_format}"},
                        "view": ["btn_enable", "btn_disable", "btn_back"],
                        "btn_enable": {
                            "db": ["link.options.allowSocialLinks", True, None],
                            "return": 2
                        },
                        "btn_disable": {
                            "db": ["link.options.allowSocialLinks", False, None],
                            "return": 2
                        }
                    }
                }
            },
            "ping" : {
                "embed": self.MAIN_SCREEN,
                "view": ["btn_switch", "btn_edit", "return"],
                "btn_edit": {
                    "embed": {"description": "Choose plugin setting from the list to continue."},
                    "view": [{"name": "slc_select", "kwargs": {"options" : [
                        discord.SelectOption(label="Status", value="status", description="Enable/Disable plugin"), 
                        discord.SelectOption(label="Reply Pings", value="reply", description="Enable/Disable reply ping detection."), 
                        discord.SelectOption(label="Ignored Channels", value="channels", description="Edit ignored channels list."), 
                        discord.SelectOption(label="Rules/Settings", value="rules", description="Create, remove, update rules.")]}}, "btn_back"],
                    "status": {
                        "embed": {"description": "Click on the buttons below to `Enable/Disable` **Ping Protection!**\n**Current:** {status:boolean_format?option='switch'&discord_format}"},
                        "view": ["btn_enable", "btn_disable", "btn_back"],
                        "btn_enable": {
                            "db": ["ping.status", True, None],
                            "return": 2
                        },
                        "btn_disable": {
                            "db": ["ping.status", False, None],
                            "return": 2
                        }
                    },
                    "reply": {
                        "embed": {"description": "Click on the buttons below to `Enable/Disable` **Reply Ping Detection**\n**Current:** {detectReplyPings:boolean_format?option='switch'&discord_format}"},
                        "view": ["btn_enable", "btn_disable", "btn_back"],
                        "btn_enable": {
                            "db": ["ping.detectReplyPings", True, None],
                            "return": 2
                        },
                        "btn_disable": {
                            "db": ["ping.detectReplyPings", False, None],
                            "return": 2
                        }
                    },
                    "channels": {
                        "embed": {"description": "Choose action setting from the buttons."},
                        "view": ["btn_add", "btn_remove", "btn_back"],
                        "btn_add": {
                            "embed": {"description": "Choose **Text Channel** that you want to add to the list.\n**Current:**\n{ignoredChannels:id_format?option='channel'&list_format}"},
                            "view":  [{"name": "slc_channel", "kwargs": {"channel_types": [discord.ChannelType.text]}}, "btn_back"],
                            "slc_channel": {
                                "db": ["ping.ignoredChannels", "SELF:1", "append"],
                                "return": 1
                            }
                        },
                        "btn_remove": {
                            "embed": {"description": "Choose **Text Channel** that you want to remove from the list.\n**Current:**\n{ignoredChannels:id_format?option='channel'&list_format}"},
                            "view":  [{"name": "slc_channel", "kwargs": {"channel_types": [discord.ChannelType.text]}}, "btn_back"],
                            "slc_channel": {
                                "db": ["ping.ignoredChannels", "SELF:1", "remove"],
                                "return": 1
                            }
                        }
                    },
                    "rules": {
                        "embed": {"description": "Choose a rule from the list or create a new one."},
                        "view": [{"name": "slc_select", "generate": {"path": "ping.rules", "type": discord.SelectOption, "example": dict(label="PLACEHOLDER", value="PLACEHOLDER"), "key": "options"}}, "btn_back"],
                        "*": {
                            "embed": {"description": "Is this the right rule? Click **edit** if so!"},
                            "view": ["btn_edit", "btn_back"]
                        },
                    }
                }

            },
            "auto_delete" : {
                "view" : ["switch", "create", "edit", "remove", "return"]
            },
            "auto_slowmode" : {
                "view" : ["switch", "create", "edit", "remove", "return"]
            },
        }
        
        self.config_history: list[dict] = [self.config]
        self.current_config: dict = self.config
        self.footer_data: bool | None = None
        self.local_db: dict[str, typing.Any] = {}

    # moves back and forth in the config dict tree
    def navigate(self, key: str = None) -> dict:
        if key:
            if cnf := self.config_history[-1].get(key):
                self.config_history.append(cnf)
                self.current_config = cnf
                return self.current_config

        else:
            self.config_history.pop()
            self.current_config = self.config_history[-1]
            return self.current_config

    #  resets everything - less bugs when switching options/switches
    def reset_configurator(self) -> None:
        self.config_history = [self.config]
        self.current_config = self.config

    # formats embed
    def format_embed(self, embed_data: dict[str, typing.Any], footer_data: bool = False) -> discord.Embed:
        try:
            # base embed
            BASE_EMBED: dict = dict(title="Configuration Wizard 🪄", timestamp=self.shared._datetime(), color=discord.Colour.dark_embed())
            
            # embed creation and updating
            if isinstance(embed_data, dict):
                dict_embed: dict[str, typing.Any] = {**BASE_EMBED, **embed_data}
                for k,v in dict_embed.items():
                    if isinstance(v, str):
                        dict_embed[k] = self.shared.string_formats.format(v, self.guild_db.get(self.option))

                EMBED: discord.Embed = discord.Embed(**dict_embed)
            else:
                self.shared.logger.log(f"@Configurator.format_embed > Wrong datatype for `embed_data`. Required `dict`, got {type(embed_data)}.", "ERROR")
                return
            
            if footer_data:
                EMBED.set_footer(text="✅ Sucessfully applied configuration settings." if self.footer_data else "❌ Failed to apply configuration settings.")
            else:
                EMBED.set_footer(text=f"Configuration for {self.view.global_config.get(self.option)["name"]}")
            
            return EMBED
        except Exception as error:
            self.shared.logger.log(f"@Configurator.format_embed > {type(error).__name__}: {error}", "ERROR")

    # generates discord view items for dynamic configurator updates
    def item_generator(self, config: dict[str, typing.Any]) -> list:
        if isinstance(config, dict):
            keys: list[str] = config.get("path").split(".")
            database: dict[str, str | dict[str, str | int] | int] = self.guild_db
            for key in keys:
                if key in database:
                    database = database[key]
                else:
                    raise MemoryError(f"Failed to reach value specified: {config.get("path")}")

            if isinstance(database, dict):
                items: list[discord.ui.Item] = []
                for item in database.keys():
                    items.append(config["type"](**{k: v.replace("PLACEHOLDER", item) for k,v in config["example"].items()}))
                return items
            else:
                raise ValueError(f"Wanted `dict`, got {type(database)}")
        else:
            raise ValueError(f"Requested `dict`, got {type(config)}")

    # checks for "view" key and iterates and appends pre-created view items
    def handle_view(self):
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
            object: typing.Callable | None
            kwargs: dict[str, typing.Any]

            if isinstance(item, dict):
                object, kwargs = discord_items.get(item.get("name"), (None, {}))
                
                if example := item.get("generate"):
                    kwargs.update({example.get("key"): self.item_generator(example)})

                if override := item.get("kwargs"):
                    kwargs.update(override)
            
            elif isinstance(item, str):
                object, kwargs = discord_items.get(item, (None, None))
            
            else:
                raise ValueError("Not a `dict` or `str`. Bad config.")
            
            if not object or not kwargs:
                continue
            try:
                self.view.add_item(object(**kwargs))
            except: pass
        
        return self.view

    # logic that handles saving to database
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
            
            # db value:
            if isinstance(database[keys[-1]], (list, dict)):
                if func:
                    data: dict[str, typing.Any] | list[typing.Any] = database[keys[-1]]
                    
                    try:
                        getattr(data, func)(value)
                    except: pass

                    if isinstance(data, list):
                        # remove duplicates - hacky but idc
                        data = list(set(data))

                    database[keys[-1]] = data            
                else:
                    raise AttributeError(f"Missing function type argument on {type(database[keys[-1]])} type. > Path: {path}")
            else:
                database[keys[-1]] = value

            self.shared.db.save_data(interaction.guild.id, self.guild_db)
            self.footer_data = True
            return

        interaction_data: dict[str, str | list[str] | dict[str, typing.Any]] =  dict(interaction.data)

        if item_id.startswith("btn_"):
            config_rule: tuple[typing.Any, str, str] = self.current_config.get("db")
            value = config_rule[1]

        elif item_id.startswith("slc_"):
            config_rule: tuple[typing.Any, str, str] = self.current_config.get("db")

            all_values: list[int | str] = [ast.literal_eval(value) for value in interaction_data.get("values")]
            value: list[typing.Any] = all_values if config_rule[1] == "SELF:*" else index_numbers if len(index_numbers := all_values[:int(config_rule[1].split(":")[-1])]) > 1 else index_numbers[0]
            
        save_to_database(path=config_rule[0], value=value, func=config_rule[2])

    # if option provided exists in config, display, otherwise display FALLBACK embed - no config for that option
    async def handle_first_screen(self) -> None:
        
        if self.navigate(self.option):
            await self.view.update_message(self.interaction, {"embed": self.format_embed(self.MAIN_SCREEN), "view": self.handle_view()})
        else:
            await self.view.update_message(self.interaction, {"embed": self.format_embed(self.FALLBACK), "view": self.view.clear_items().create_back_button()})

    async def handle_interaction(self, custom_id: str, interaction: discord.Interaction, view) -> None:
        #check for view and database
        if not view:
            raise ValueError("No view recieved.")
        if not (guild_db := self.shared.db.load_data(interaction.guild.id)):
            raise ValueError(f"No database data found, corrupted or missing database for: {interaction.guild.name} ({interaction.guild.id}) ?")

        # setting global values per interaction
        self.view: AdvancedPaginator = view
        self.option: str = self.view.current_position
        self.guild_db: dict[str, str | dict[str, str | int] | int] = guild_db
        self.interaction: discord.Interaction[discord.Client] = interaction

        # start handler
        if custom_id.endswith(":START"):
            self.reset_configurator()
            await self.handle_first_screen()

        # just switch handler
        elif custom_id.endswith(":btn_switch"):
            self.reset_configurator()
            self.guild_db[self.option]["status"] = not self.guild_db[self.option]["status"]
            self.shared.db.save_data(interaction.guild.id, self.guild_db)
            await self.handle_first_screen()

        else:
            # actual logic and resloving
            item_id: str = custom_id.split(":")[-1]

            # on btn_back, goes one navigation back
            if item_id == "btn_back":
                self.navigate(None)
            
            #TODO: fix nonsense if we use custom select
            elif item_id == "slc_select":
                if not self.navigate(interaction.data.get("values")[0]):
                    self.navigate("*")

            # actual navigation
            elif self.navigate(item_id):
                # checks if the value exists for saving in local db
                if self.current_config.get("db"):
                    self.handle_db(item_id, interaction)
            else:
                raise NotImplementedError("Failed to navigate interaction in the config.")

            old_cfg = self.current_config
            # looking for "return" setting
            if repeat_return := self.current_config.get("return"):
                # returning x times (value of the return key)
                for _ in range(repeat_return):
                    self.navigate(None)

            # display logic -> find embed and view and display
            if self.current_config.get("embed") and self.current_config.get("view"):
                await self.view.update_message(interaction, dict(embed=self.format_embed(self.current_config.get("embed"),  old_cfg.get("db")), view=self.handle_view()))
            
            # reset
            self.footer_data = None

"""
{
    "general": {
        "allowAdminEditing": false,
        "staffRole": 1002486727081992273,
        "staffChannel": 1037720138335662141,
        "adminRole": 996878384867065967,
        "adminChannel": 1226136202864754779,
        "language": "US/en",
        "status": true
    },
    "cmd": {
        "logCmdExecution": true,
        "failedCmdExecution": true,
        "cmdExecutionLogChannel": 1043532394042503198
    },
    "alt": {
        "status": true,
        "log_channel": 991436211807854642
    },
    "imper": {
        "status": true,
        "log_channel": 1015937645135790120
    },
    "ai": {
        "status": true,
        "log_channel": null,
        "talkChannels": [
            1032353612665466992,
            1037720138335662141,
            1043532394042503198
        ]
    },
    "automod": {
        "status": false,
        "log_channel": 1015937645135790120,
        "rules": {}
    },
    "link": {
        "status": true,
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
    "auto_delete": {
        "status": true,
        "log_channel": 1015937645135790120,
        "monitored": {
            "1015937738823970856": 313
        }
    },
    "auto_slowmode": {
        "status": true,
        "log_channel": 1015937645135790120,
        "monitored": {
            "1032353612665466992": 31235,
            "1015937645135790120": 145
        }
    },
    "reaction": {
        "status": true,
        "log_channel": 1015937645135790120,
        "reactionBanRole": 1203444406108295258
    },
    "QOFTD": {
        "status": true,
        "log_channel": 1032353612665466992
    },
    "fan_art": {
        "status": false,
        "log_channel": null,
        "montired": []
    },
    "responder": {
        "status": false
    },
    "leveling_system": {
        "status": false,
        "log_channel": null,
        "levels": {
            "message": false,
            "voice": false,
            "reaction": false
        },
        "rewards": {
            "message": [],
            "voice": [],
            "reaction": []
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
        }
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