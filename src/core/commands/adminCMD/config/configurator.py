import sys, discord, typing, ast
sys.dont_write_bytecode = True
import src.connector as con

from discord.ui import RoleSelect, ChannelSelect, UserSelect, Select, MentionableSelect, Button, TextInput

if typing.TYPE_CHECKING:
    from .base_handler import BaseConfigCMDView

"""
embed = dict[str, str]
view = list[dict[config_discord_items] | str[discord_items]]

db = list[str, Any, str | None, str] -> [0]: path or local.[path], [1]: value > "SELF:{int|*}", [2]: func, [3]: type
["local.staff", "SELF:1", None, None] > value change
["local.staff", "SELF:1", None, "test"] > key = [1], value = local_db["pre-sets"]["test"]

generator = name, value -> placeholder `key`, `value` +optional path
modal = dict[str, str | list[TextInput]] -> custom_id: "ID:{path.to.key} | SELF"
local_db -> STATIC - perm
"""


class Configurator:
    def __init__(self, guild_id: int) -> None:
        self.shared: con.Shared = con.shared
        self.reset_configurator()

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
                        discord.SelectOption(label="Staff/Mod role", value="staff_role", description="Set Mod/Staff's role, this is REQUIRED."),
                        discord.SelectOption(label="Staff/Mod chat", value="staff_chat", description="Set Mod/Staff's channel, this is REQUIRED."),
                        discord.SelectOption(label="Admin role", value="admin_role", description="Set Admin's role, this is REQUIRED."),
                        discord.SelectOption(label="Admin chat", value="admin_chat", description="Set Admin's channel, this is REQUIRED.")],
                        "placeholder": "Choose selection (you might need to scroll)"}}, "btn_back"],
                    "status": {
                        "embed": {"description": "Click on the buttons below to `Enable/Disable` **Bot!**\n**Current:** {general[status]:boolean_format?option='switch'&discord_format}"},
                        "view": ["btn_enable", "btn_disable", "btn_back"],
                        "btn_enable": {
                            "db": [["general", "status"], True, None, None],
                            "return": 2
                        },
                        "btn_disable": {
                            "db": [["general", "status"], False, None, None],
                            "return": 2
                        }
                    },
                    "staff_role": {
                        "embed": {"description": "Choose **Role** that will be used as **Staff/Mod Role**.\n**Current:** {general[staffRole]:id_format?option='role'}"},
                        "view": ["slc_role", "btn_back"],
                        "slc_role": {
                            "db": [["general", "staffRole"], "SELF:1", None, None],
                            "return": 2
                        }
                    },
                    "staff_chat": {
                        "embed": {"description": "Choose **Text Channel** that will be used as **Staff/Mod Channel**.\n**Current:** {general[staffChannel]:id_format?option='channel'}"},
                        "view": [{"name": "slc_channel", "kwargs": {"channel_types": [discord.ChannelType.text]}}, "btn_back"],
                        "slc_channel": {
                            "db": [["general", "staffChannel"], "SELF:1", None, None],
                            "return": 2
                        }
                    },
                    "admin_role": {
                        "embed": {"description": "Choose **Role** that will be used as **Admin Role**.\n**Current:** {general[adminRole]:id_format?option='role'}"},
                        "view": ["slc_role", "btn_back"],
                        "slc_role": {
                            "db": [["general", "adminRole"], "SELF:1", None, None],
                            "return": 2
                        }
                    },
                    "admin_chat": {
                        "embed": {"description": "Choose **Text Channel** that will be used as **Admin Channel**.\n**Current:** {general[adminChannel]:id_format?option='channel'}"},
                        "view": [{"name": "slc_channel", "kwargs": {"channel_types": [discord.ChannelType.text]}}, "btn_back"],
                        "slc_channel": {
                            "db": [["general", "adminChannel"], "SELF:1", None, None],
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
                        "embed": {"description": "Click on the buttons below to `Enable/Disable` **Alt detection!**\n**Current:** {alt[status]:boolean_format?option='switch'&discord_format}"},
                        "view": ["btn_enable", "btn_disable", "btn_back"],
                        "btn_enable": {
                            "db": [["alt", "status"], True, None, None],
                            "return": 2
                        },
                        "btn_disable": {
                            "db": [["alt", "status"], False, None, None],
                            "return": 2
                        }
                    },
                    "log_channel": {
                        "embed": {"description": "Choose **Text Channel** that will be used to log events.\n**Current:** {alt[log_channel]:id_format?option='channel'}"},
                        "view": [{"name": "slc_channel", "kwargs": {"channel_types": [discord.ChannelType.text]}}, "btn_back"],
                        "slc_channel": {
                            "db": [["alt", "log_channel"], "SELF:1", None, None],
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
                        "embed": {"description": "Click on the buttons below to `Enable/Disable` **Impersonator detection!**\n**Current:** {imper[status]:boolean_format?option='switch'&discord_format}"},
                        "view": ["btn_enable", "btn_disable", "btn_back"],
                        "btn_enable": {
                            "db": [["imper", "status"], True, None, None],
                            "return": 2
                        },
                        "btn_disable": {
                            "db": [["imper", "status"], False, None, None],
                            "return": 2
                        }
                    },
                    "log_channel": {
                        "embed": {"description": "Choose **Text Channel** that will be used to log events.\n**Current:** {imper[log_channel]:id_format?option='channel'}"},
                        "view": [{"name": "slc_channel", "kwargs": {"channel_types": [discord.ChannelType.text]}}, "btn_back"],
                        "slc_channel": {
                            "db": [["imper", "log_channel"], "SELF:1", None, None],
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
                        "embed": {"description": "Click on the buttons below to `Enable/Disable` **AI!**\n**Current:** {general[status]:boolean_format?option='switch'&discord_format}"},
                        "view": ["btn_enable", "btn_disable", "btn_back"],
                        "btn_enable": {
                            "db": [["ai", "status"], True, None, None],
                            "return": 2
                        },
                        "btn_disable": {
                            "db": [["ai", "status"], False, None, None],
                            "return": 2
                        }
                    },
                    "respond": {
                        "embed": {"description": "Choose action setting from the buttons down below."},
                        "view": ["btn_add", "btn_remove", "btn_back"],
                        "btn_add": {
                            "embed": {"description": "Choose **Text Channel** that you want to add to the list.\n**Current:**\n{ai[talkChannels]:id_format?option='channel'&list_format}"},
                            "view":  [{"name": "slc_channel", "kwargs": {"channel_types": [discord.ChannelType.text]}}, "btn_back"],
                            "slc_channel": {
                                "db": [["ai", "talkChannels"], "SELF:1", "append", None],
                                "return": 1
                            }
                        },
                        "btn_remove": {
                            "embed": {"description": "Choose **Text Channel** that you want to remove from the list.\n**Current:**\n{ai[talkChannels]:id_format?option='channel'&list_format}"},
                            "view":  [{"name": "slc_channel", "kwargs": {"channel_types": [discord.ChannelType.text]}}, "btn_back"],
                            "slc_channel": {
                                "db": [["ai", "talkChannels"], "SELF:1", "remove", None],
                                "return": 1
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
                        "embed": {"description": "Click on the buttons below to `Enable/Disable` **Link Protection!**\n**Current:** {link[status]:boolean_format?option='switch'&discord_format}"},
                        "view": ["btn_enable", "btn_disable", "btn_back"],
                        "btn_enable": {
                            "db": [["link", "status"], True, None, None],
                            "return": 2
                        },
                        "btn_disable": {
                            "db": [["link", "status"], False, None, None],
                            "return": 2
                        }
                    },
                    "log_channel": {
                        "embed": {"description": "Choose **Text Channel** that will be used to log events.\n**Current:** {link[log_channel]:id_format?option='channel'}"},
                        "view": [{"name": "slc_channel", "kwargs": {"channel_types": [discord.ChannelType.text]}}, "btn_back"],
                        "slc_channel": {
                            "db": [["link", "log_channel"], "SELF:1", None, None],
                            "return": 2
                        }
                    },
                    "dc_invites": {
                        "embed": {"description": "Click on the buttons below to `Allow/Disallow` **Discord Invite Links**\n**Current:** {link[options][allowDiscordInvites]:boolean_format?option='switch'&discord_format}"},
                        "view": ["btn_enable", "btn_disable", "btn_back"],
                        "btn_enable": {
                            "db": [["link", "options", "allowDiscordInvites"], True, None, None],
                            "return": 2
                        },
                        "btn_disable": {
                            "db": [["link", "options", "allowDiscordInvites"], False, None, None],
                            "return": 2
                        }
                    },
                    "dc_gifts": {
                        "embed": {"description": "Click on the buttons below to `Allow/Disallow` **Discord Gift Links**\n**Current:** {link[options][allowNitroGifts]:boolean_format?option='switch'&discord_format}"},
                        "view": ["btn_enable", "btn_disable", "btn_back"],
                        "btn_enable": {
                            "db": [["link", "options", "allowNitroGifts"], True, None, None],
                            "return": 2
                        },
                        "btn_disable": {
                            "db": [["link", "options", "allowNitroGifts"], False, None, None],
                            "return": 2
                        }
                    },
                    "socials": {
                        "embed": {"description": "Click on the buttons below to `Allow/Disallow` **Social Account Links**\n**Current:** {link[options][allowSocialLinks]:boolean_format?option='switch'&discord_format}"},
                        "view": ["btn_enable", "btn_disable", "btn_back"],
                        "btn_enable": {
                            "db": [["link", "options", "allowSocialLinks"], True, None, None],
                            "return": 2
                        },
                        "btn_disable": {
                            "db": [["link", "options", "allowSocialLinks"], False, None, None],
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
                        "embed": {"description": "Click on the buttons below to `Enable/Disable` **Ping Protection!**\n**Current:** {ping[status]:boolean_format?option='switch'&discord_format}"},
                        "view": ["btn_enable", "btn_disable", "btn_back"],
                        "btn_enable": {
                            "db": [["ping", "status"], True, None, None],
                            "return": 2
                        },
                        "btn_disable": {
                            "db": [["ping", "status"], False, None, None],
                            "return": 2
                        }
                    },
                    "reply": {
                        "embed": {"description": "Click on the buttons below to `Enable/Disable` **Reply Ping Detection**\n**Current:** {ping[detectReplyPings]:boolean_format?option='switch'&discord_format}"},
                        "view": ["btn_enable", "btn_disable", "btn_back"],
                        "btn_enable": {
                            "db": [["ping", "detectReplyPings"], True, None, None],
                            "return": 2
                        },
                        "btn_disable": {
                            "db": [["ping", "detectReplyPings"], False, None, None],
                            "return": 2
                        }
                    },
                    "channels": {
                        "embed": {"description": "Choose action setting from the buttons."},
                        "view": ["btn_add", "btn_remove", "btn_back"],
                        "btn_add": {
                            "embed": {"description": "Choose **Text Channel** that you want to add to the list.\n**Current:**\n{ping[ignoredChannels]:id_format?option='channel'&list_format}"},
                            "view":  [{"name": "slc_channel", "kwargs": {"channel_types": [discord.ChannelType.text]}}, "btn_back"],
                            "slc_channel": {
                                "db": [["ping", "ignoredChannels"], "SELF:1", "append", None],
                                "return": 1
                            }
                        },
                        "btn_remove": {
                            "embed": {"description": "Choose **Text Channel** that you want to remove from the list.\n**Current:**\n{ping[ignoredChannels]:id_format?option='channel'&list_format}"},
                            "view":  [{"name": "slc_channel", "kwargs": {"channel_types": [discord.ChannelType.text]}}, "btn_back"],
                            "slc_channel": {
                                "db": [["ping", "ignoredChannels"], "SELF:1", "remove", None],
                                "return": 1
                            }
                        }
                    },
                    "rules": {
                        "embed": {"description": "Choose a rule from the list or create a new one."},
                        "view": ["btn_create", "btn_remove", {"name": "slc_select", "generate": {"path": ["ping", "rules"], "type": discord.SelectOption, "example": dict(label="{key}", value="{key}"), "key": "options"}}, "btn_back"],
                        "btn_create": {
                            "modal": {"title": "Creating: Ping protection rule", "custom_id": "mdl_create_ping_rule", "text_inputs": [TextInput(label="Name of the rule:", custom_id="txt_ping", max_length=15)]},
                            "mdl_create_ping_rule": {
                                "txt_ping": {
                                    "db": [["ping", "rules"], "SELF:1", None, "pingCreate"],
                                    "return": 3
                                }
                            }  
                        },
                        "*": {
                            "db_path": ["ping", "rules", "SELF:1"],
                            "embed": {"description": "## Editing rule:\n\n**Role:**           {@LOCAL[role]:id_format?option='role'}\n**Bypass role:**    {@LOCAL[bypass]:id_format?option='role'}\n**Ping staff:**     {@LOCAL[ping]:boolean_format?option='y/n'&discord_format}\n**Log message:**    {@LOCAL[log]:boolean_format?option='y/n'&discord_format}\n**Log channel:**    {@LOCAL[logChannel]:id_format?option='channel'}\n**Delete message:** {@LOCAL[delete]:boolean_format?option='y/n'&discord_format}"},
                            "view": [{"type": Button, "kwargs": dict(custom_id="CONFIG:btn_prt_role", label="Protected Role", style=discord.ButtonStyle.green)},
                                     {"type": Button, "kwargs": dict(custom_id="CONFIG:btn_bypass_role", label="Bypass Role", style=discord.ButtonStyle.blurple)},
                                     {"type": Button, "kwargs": dict(custom_id="CONFIG:btn_mention", label="Ping Staff", style=discord.ButtonStyle.gray)},
                                     {"type": Button, "kwargs": dict(custom_id="CONFIG:btn_log_channel", label="Log Channel", style=discord.ButtonStyle.blurple)},
                                     {"type": Button, "kwargs": dict(custom_id="CONFIG:btn_log", label="Log Event", style=discord.ButtonStyle.gray)},
                                     {"type": Button, "kwargs": dict(custom_id="CONFIG:btn_delete", label="Delete Message", style=discord.ButtonStyle.red)}, "btn_back"],
                            
                            "btn_prt_role": {
                                    "embed": {"description": "Choose **one Role** that will this rule **protect**.\n**Current:** {@LOCAL[role]:id_format?option='channel'}"},
                                    "view": ["slc_role", "btn_back"],
                                    "slc_role": {
                                        "db": [["local", "role"], "SELF:1", None, None],
                                        "return": 2
                                    }
                                },
                            "btn_bypass_role": {
                                    "embed": {"description": "Choose **one Role** that will **bypass** this rule.\n**Current:** {@LOCAL[bypass]:id_format?option='role'}"},
                                    "view": ["slc_role", "btn_back"],
                                    "slc_role": {
                                        "db": [["local", "bypass"], "SELF:1", None, None],
                                        "return": 2
                                    }
                                },
                            "btn_mention": {
                                    "embed": {"description": "Click on the buttons below to `Enable/Disable` **staff ping**.\n**Current:** {@LOCAL[ping]:boolean_format?option='switch'&discord_format}"},
                                    "view": ["btn_enable", "btn_disable", "btn_back"],
                                    "btn_enable": {
                                        "db": [["local", "ping"], True, None, None],
                                        "return": 2
                                    },
                                    "btn_disable": {
                                        "db": [["local", "ping"], False, None, None],
                                        "return": 2
                                    }
                                },
                            "btn_log_channel": {
                                    "embed": {"description": "Choose **Text Channel** that will be used to log events.\n**Current:** {@LOCAL[logChannel]:id_format?option='channel'}"},
                                    "view": [{"name": "slc_channel", "kwargs": {"channel_types": [discord.ChannelType.text]}}, "btn_back"],
                                    "slc_channel": {
                                        "db": [["local", "logChannel"], "SELF:1", None, None],
                                        "return": 2
                                    }
                                },
                            "btn_log": {
                                    "embed": {"description": "Click on the buttons below to `Enable/Disable` **logging**.\n**Current:** {@LOCAL[log]:boolean_format?option='switch'&discord_format}"},
                                    "view": ["btn_enable", "btn_disable", "btn_back"],
                                    "btn_enable": {
                                        "db": [["local", "log"], True, None, None],
                                        "return": 2
                                    },
                                    "btn_disable": {
                                        "db": [["local", "log"], False, None, None],
                                        "return": 2
                                    }
                                },
                            "btn_delete": {
                                    "embed": {"description": "Click on the buttons below to `Enable/Disable` **message deleting.**\n**Current:** {@LOCAL[delete]:boolean_format?option='switch'&discord_format}"},
                                    "view": ["btn_enable", "btn_disable", "btn_back"],
                                    "btn_enable": {
                                        "db": [["local", "delete"], True, None, None],
                                        "return": 2
                                    },
                                    "btn_disable": {
                                        "db": [["local", "delete"], False, None, None],
                                        "return": 2
                                    }
                                }
                        },
                        "btn_remove": {
                            "embed": {"description": "Choose a **Rule** that you want to delete."},
                            "view": [{"name": "slc_select", "generate": {"path": ["ping", "rules"], "type": discord.SelectOption, "example": dict(label="{key}", value="{key}"), "key": "options"}}, "btn_back"],
                            "*": {
                                "db": [["ping", "rules"], "SELF:1", "pop", None],
                                "return": 1
                            }
                        }
                    }
                }

            },
            "auto_delete" : {
                "embed": self.MAIN_SCREEN,
                "view" : ["btn_switch", "btn_edit", "return"],
                "btn_edit": {
                    "embed": {"description": "Choose plugin setting from the list to continue."},
                    "view": [{"name": "slc_select", "kwargs" : {"options" : [
                        discord.SelectOption(label="Status", value="status", description="Enable/Disable plugin"), 
                        discord.SelectOption(label="Monitored channels", description="Monitored channels settings.", value="monitored")]}}, "btn_back"],
                    "status": {
                        "embed": {"description": "Click on the buttons below to `Enable/Disable` **Auto Delete!**\n**Current:** {auto_delete[status]:boolean_format?option='switch'&discord_format}"},
                        "view": ["btn_enable", "btn_disable", "btn_back"],
                        "btn_enable": {
                            "db": [["auto_delete", "status"], True, None, None],
                            "return": 2
                        },
                        "btn_disable": {
                            "db": [["auto_delete", "status"], False, None, None],
                            "return": 2
                        }
                    },
                    "monitored": {
                        "embed": {"description": "Choose **Text channel** to edit auto delete time or use buttons to `create/remove` rules.\n**Current:**\n{auto_delete[monitored]:id_format?option='channel'|time_converter&discord_format>list_format}"},
                        "view": ["btn_create", "btn_remove", {"name": "slc_select", "generate": {"path": ["auto_delete", "monitored"], "type": discord.SelectOption, "example": dict(label="{key:resolve_id?guild=%d,var='name'}" % guild_id, value="{key}"), "key": "options"}}, "btn_back"],
                        "*": {
                            "db_path": ["auto_delete", "monitored", "SELF:1"],
                            "modal": {"title": "Updating: Rule time.", "custom_id": "mdl_create", "text_inputs": [TextInput(label="Time (number only) in seconds:", custom_id="txt_autoDelete", max_length=5)]},
                            "mdl_create": {
                                "txt_autoDelete": {
                                    "db": [["local"], "SELF:1", None, None],
                                    "return": 3
                                }                                    
                            }
                        },
                        "btn_create": {
                            "embed": {"description": "Choose **Text Channel** that you want to add to the list.\n**Current:**\n{auto_delete[monitored]:id_format?option='channel'|time_converter&discord_format>list_format}"},
                            "view":  [{"name": "slc_channel", "kwargs": {"channel_types": [discord.ChannelType.text]}}, "btn_back"],
                            "*": {
                                "db": [["auto_delete", "monitored"], "SELF:1", None, "autoDelete"],
                                "return": 1
                            }
                        },
                        "btn_remove": {
                            "embed": {"description": "Choose a **Rule** that you want to delete.\n**Current:**\n{auto_delete[monitored]:id_format?option='channel'|time_converter&discord_format>list_format}"},
                            "view": [{"name": "slc_select", "generate": {"path": ["auto_delete", "monitored"], "type": discord.SelectOption, "example": dict(label="{key:resolve_id?guild=%d,var='name'}" % guild_id, value="{key}"), "key": "options"}}, "btn_back"],
                            "*": {
                                "db": [["auto_delete", "monitored"], "SELF:1", "pop", None],
                                "return": 1
                            }
                        }
                    }
                }
            },
            "auto_slowmode" : {
                "embed": self.MAIN_SCREEN,
                "view" : ["btn_switch", "btn_edit", "return"],
                "btn_edit": {
                    "embed": {"description": "Choose plugin setting from the list to continue."},
                    "view": [{"name": "slc_select", "kwargs" : {"options" : [
                        discord.SelectOption(label="Status", value="status", description="Enable/Disable plugin"), 
                        discord.SelectOption(label="Monitored channels", description="Monitored channels settings.", value="monitored")]}}, "btn_back"],
                    "status": {
                        "embed": {"description": "Click on the buttons below to `Enable/Disable` **Auto Slowmode!**\n**Current:** {auto_slowmode[status]:boolean_format?option='switch'&discord_format}"},
                        "view": ["btn_enable", "btn_disable", "btn_back"],
                        "btn_enable": {
                            "db": [["auto_slowmode", "status"], True, None, None],
                            "return": 2
                        },
                        "btn_disable": {
                            "db": [["auto_slowmode", "status"], False, None, None],
                            "return": 2
                        }
                    },
                    "monitored": {
                        "embed": {"description": "Choose **Text channel** to edit auto slowmode time or use buttons to `create/remove` rules.\n**Current:**\n{auto_slowmode[monitored]:id_format?option='channel'|time_converter&discord_format>list_format}"},
                        "view": ["btn_create", "btn_remove", {"name": "slc_select", "generate": {"path": ["auto_slowmode", "monitored"], "type": discord.SelectOption, "example": dict(label="{key:resolve_id?guild=%d,var='name'}" % guild_id, value="{key}"), "key": "options"}}, "btn_back"],
                        "*": {
                        "db_path": ["auto_slowmode", "monitored", "SELF:1"],
                            "modal": {"title": "Updating: Default chat slowmode time.", "custom_id": "mdl_create", "text_inputs": [TextInput(label="Time (number only) in seconds:", custom_id="txt_autoSlowmode", max_length=5)]},
                            "mdl_create": {
                                "txt_autoSlowmode": {
                                    "db": [["local"], "SELF:1", None, None],
                                    "return": 3
                                }                                    
                            }
                        },
                        "btn_create": {
                            "embed": {"description": "Choose **Text Channel** that you want to add to the list.\n**Current:**\n{auto_slowmode[monitored]:id_format?option='channel'|time_converter&discord_format>list_format}"},
                            "view":  [{"name": "slc_channel", "kwargs": {"channel_types": [discord.ChannelType.text]}}, "btn_back"],
                            "*": {
                                "db": [["auto_slowmode", "monitored"], "SELF:1", None, "autoSlowmode"],
                                "return": 1
                            }
                        },
                        "btn_remove": {
                            "embed": {"description": "Choose a **Rule** that you want to delete.\n**Current:**\n{auto_slowmode[monitored]:id_format?option='channel'|time_converter&discord_format>list_format}"},
                            "view": [{"name": "slc_select", "generate": {"path": ["auto_slowmode", "monitored"], "type": discord.SelectOption, "example": dict(label="{key:resolve_id?guild=%d,var='name'}" % guild_id, value="{key}"), "key": "options"}}, "btn_back"],
                            "*": {
                                "db": [["auto_slowmode", "monitored"], "SELF:1", "pop", None],
                                "return": 1
                            }
                        }
                    }
                }
            }
        }


    # method that moves inside the config and databases (dicts)
    def db_traversal(self, dictionary: dict[str, typing.Any], path: str | list[str], _slice: slice = slice(None, None), _sep: str = ".") -> dict[str, typing.Any]:
        current_db: dict[str, typing.Any] = dictionary
        path = path.split(_sep) if isinstance(path, str) else path

        for key in path[_slice]:
            if key in current_db:
                current_db = current_db[key]
            else:
                raise MemoryError(f"Failed to reach value specified: `{key}` on `{path}`")
        return current_db

    # handler for SELF:[INT&*] argument
    def list_slicing(self, iterable: list | tuple, argument: str) -> list | typing.Any:
        if not isinstance(iterable, (list, tuple)):
            return iterable
        return iterable if argument.endswith(":*") else index_numbers if len(index_numbers := iterable[:int(argument.split(":")[-1])]) > 1 else index_numbers[0]

    # resets the local database (module switching)
    def reset_configurator(self) -> None:
        self.local_db: dict[str, list[str] | str | dict[str, typing.Any]] = {
            "local_path": [],
            "db_path": [],
            "footer": None,
            "db": None,
            "pre-sets": {
                "pingCreate": {"role": None, "ping": False, "log": False, "logChannel": None, "delete": False, "bypass": None},
                "autoDelete": 0,
                "autoSlowmode": 0               
            }
        }
        self.shared.logger.log(f"@Configurator.reset_configurator > Reset configurator", "TESTING")
    
    # navigation for interaction
    def navigate(self, custom_id: str, value: str = None) -> dict:
        if not custom_id:
            self.shared.logger.log(f"@Configurator.navigate > Going back", "TESTING")
            self.local_db["local_path"].pop(-1)

        current_config: dict[str, typing.Any] = self.db_traversal(self.config, self.local_db["local_path"])

        if custom_id:
            if custom_id and current_config.get(custom_id):
                segment: str = custom_id
            elif value and current_config.get(str(value)):
                segment: str = str(value)
            elif current_config.get("*"):
                segment: str = "*"
            else:
                raise LookupError(f"Could not navigate the interaction in config. {custom_id}: {value} >> Current keys: {list(current_config.keys())}")

            self.local_db["local_path"].append(segment)
            current_config = current_config[segment]
            
            self.shared.logger.log(f"@Configurator.navigate > Got segment: {segment}", "TESTING")

        # local database path        
        if (old_path := self.local_db["db"]) and not custom_id:
            [self.local_db["db_path"].pop() for _ in range(len(old_path))] # idk if okay <<    
            
        self.local_db["db"] = None

        if db_path := current_config.get("db_path"):
            path: list[str] = [self.list_slicing(value, segment) if ":" in segment else segment for segment in db_path]  

            if custom_id:
                self.local_db["db_path"].extend(path)
            self.local_db["db"] = path

        # database execution
        if db_config := current_config.get("db"):
            self.handle_db(custom_id, db_config, extra=value)

        return current_config

    # formats embed - supported placeholders and merging
    def format_embed(self, embed_data: dict[str, typing.Any]) -> discord.Embed:
        BASE_EMBED: dict = dict(title="Configuration Wizard 🪄", timestamp=self.shared.time.datetime(), color=discord.Colour.dark_embed())
        
        if isinstance(embed_data, dict):
            dict_embed: dict[str, typing.Any] = BASE_EMBED | embed_data # merging 2 dicts
        else:
            dict_embed = BASE_EMBED
            
        for key, value in dict_embed.items():
            if isinstance(value, str):
                if len(db_path := self.local_db["db_path"]) >= 2:
                    # replaces @LOCAL with the database path
                    value: str = value.replace("@LOCAL", f"{db_path[0]}{"".join([f"[{x}]" for x in db_path[1:]])}")

                dict_embed[key] = self.shared.string_formats.format(value, self.guild_db)
        
        EMBED: discord.Embed = discord.Embed(**dict_embed)
        self.shared.logger.log(f"@Configurator.format_embed > Formatted embed.", "TESTING")

        if footer := self.local_db["footer"]:
            EMBED.set_footer(text=footer)
            self.local_db["footer"] = None
        else:
            EMBED.set_footer(text=f"Configuration for {self.view.global_config.get(self.option)}")
        return EMBED   

    # logic that handles saving to database
    def handle_db(self, item_id: str, database_config: dict[str, typing.Any], extra: typing.Any = None) -> None:
        self.shared.logger.log(f"@Configurator.handle_db > Got db request: ID: {item_id}", "TESTING")
        
        def save_to_database(path: list[str], value: typing.Any, func: str = None, search: str = None) -> None:
            keys: list[str] = [*self.local_db["db_path"], *path[1:]] if path[0].startswith("local") else path
            last_key: str = keys[-1]
            
            database: dict[str, str | dict[str, str | int] | int] = self.db_traversal(self.guild_db, keys, slice(None, -1))
            
            if search:
                #print(last_key, value)
                if isinstance(database[last_key], dict) and (new_value := self.local_db["pre-sets"].get(search, "UNKNOWN")) != "UNKNOWN":
                    database[last_key][str(value)] = new_value

            # db value check for method execution:
            elif isinstance(database[last_key], (list, dict)) and func:
                data: dict[str, typing.Any] | list[typing.Any] = database[last_key]

                if callable := getattr(data, func, None):
                    self.shared.logger.log(f"@Configurator.handle_db.save_to_database > Func: {callable}, value: {value}, db: {data}", "TESTING")
                    try: 
                        callable(value) if callable.__name__ not in ["pop"] else callable(str(value))
                    except: pass

                if isinstance(data, list):
                    data = list(set(data)) # remove duplicates - hacky but idc

                database[last_key] = data            
            else:
                database[last_key] = value

            self.shared.db.save_data(self.interaction.guild.id, self.guild_db)
            self.local_db["footer"] = "✅ Sucessfully applied configuration settings."

        # ---------------------------------------------------------------------------------------------------
        interaction_data: dict[str, str | list[str] | dict[str, typing.Any]] =  dict(self.interaction.data)

        if item_id.startswith("btn_"):
            values: typing.Any = database_config[1]

        elif item_id.startswith("slc_"):
            all_values: list[int | str] = []
            for value in interaction_data.get("values"):
                try:
                    all_values.append(ast.literal_eval(value))
                except:
                    all_values.append(value)
            values: list[typing.Any] = self.list_slicing(all_values, database_config[1]) if isinstance(database_config[1], str) else database_config[1]

        elif item_id.startswith("txt_"):
            if extra is not None:
                values: typing.Any = extra
            else:
                raise ValueError("Recieved `None` as value.")

        # modal arguments are being handled @ modal_interaction

        self.shared.logger.log(f"@Configurator.handle_db > Save arguments: {database_config}", "TESTING")
        return save_to_database(path=database_config[0], value=values, func=database_config[2], search=database_config[3])

    #NOTE: look at it later - new syntax possibly?
    def item_generator(self, item_config: dict[str, typing.Any]) -> list:
        self.shared.logger.log(f"@Configurator.item_generator > Generating items..", "TESTING")
        if isinstance(item_config, dict):
            database: dict[str, str | dict[str, str | int] | int] = self.db_traversal(self.guild_db, path=item_config.get("path"))

            if isinstance(database, dict):
                items: list[discord.ui.Item] = []
                for item in database.keys():
                    items.append(item_config["type"](**{k: self.shared.string_formats.format(v, {"key": item, "value": database[item]}) for k,v in item_config["example"].items()}))
                return items
            else:
                raise ValueError(f"Wanted `dict`, got {type(database)}")
        else:
            raise ValueError(f"Requested `dict`, got {type(item_config)}")

    # checks for "view" key, iterates and appends pre-created view items
    def handle_view(self, current_config: dict[str, typing.Any]):
        self.shared.logger.log(f"@Configurator.handle_view > Creating view.", "TESTING")
        discord_items: dict[str, tuple[typing.Callable, dict[str, typing.Any]]] = {
            "btn_create": (Button, dict(label="Create", custom_id="CONFIG:btn_create", style=discord.ButtonStyle.green)),
            "btn_edit": (Button, dict(label="Edit", custom_id="CONFIG:btn_edit", style=discord.ButtonStyle.gray)),
            "btn_remove": (Button, dict(label="Remove", custom_id="CONFIG:btn_remove", style=discord.ButtonStyle.red)),
            "btn_back": (Button, dict(label="Back", custom_id="CONFIG:btn_back", style=discord.ButtonStyle.red)),
            "btn_switch": (Button, dict(label="Enabled" if self.guild_db[self.option].get("status") else "Disabled", custom_id="CONFIG:btn_switch", style=discord.ButtonStyle.green if self.guild_db[self.option].get("status") else discord.ButtonStyle.red)),
            "btn_enable": (Button, dict(label="Enable", custom_id="CONFIG:btn_enable", style=discord.ButtonStyle.green)),
            "btn_disable": (Button, dict(label="Disable", custom_id="CONFIG:btn_disable", style=discord.ButtonStyle.red)),
            "btn_add": (Button, dict(label="Add", custom_id="CONFIG:btn_add", style=discord.ButtonStyle.green)),

            "slc_role": (RoleSelect, dict(custom_id="CONFIG:slc_role")),
            "slc_channel": (ChannelSelect, dict(custom_id="CONFIG:slc_channel")),
            "slc_member": (UserSelect, dict(custom_id="CONFIG:slc_member")),
            "slc_mentionable": (MentionableSelect, dict(custom_id="CONFIG:slc_mentionable")),
            "slc_select": (Select, dict(custom_id="CONFIG:slc_select")),

            "return": (self.view.create_back_button, {"item": True})
        }
        self.view.clear_items()

        for item in current_config.get("view", ()):
            object: typing.Callable | None
            kwargs: dict[str, typing.Any]

            if isinstance(item, dict):
                object, kwargs = discord_items.get(item.get("name"), (None, {}))

                if example := item.get("generate"):
                    if generated_items := self.item_generator(example):
                        kwargs.update({example.get("key"): generated_items})
                    else:
                        continue
               
                if override := item.get("kwargs"):
                    kwargs.update(override)

                if not object:
                    object = item.get("type")

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
    
    # handles modal interactions
    async def modal_interaction(self, current_config: dict[str, typing.Any]) -> None:
        clean_data: dict[str, str | list[dict]] = await self.view.create_modal(**current_config.get("modal"))
        self.shared.logger.log(f"@Configurator.modal_interaction > Got modal.", "TESTING")

        if not (current_config := self.navigate(clean_data.get("modal_id"))):
            raise NotImplementedError("Failed to find screen for the next interaction (Modal)")

        for text_input in clean_data.get("components"):
            custom_id: str = text_input.get("custom_id")
            
            try:
                input_value: typing.Any = ast.literal_eval(text_input.get("value"))
            except:
                input_value: str = text_input.get("value")            
            
            if not (screen_config := self.navigate(custom_id, input_value)):
                raise LookupError(f"Could not find required information for modal text input of: {custom_id}")    
            
            await self.create_new_screen(screen_config)
        self.shared.logger.log(f"@Configurator.modal_interaction > Handled modal's text inputs.", "TESTING")

    # creates new screen
    async def create_new_screen(self, current_config: dict[str, typing.Any]) -> None:
        if repeat_return := current_config.get("return"):
            # returning x times (value of the return key)
            for _ in range(repeat_return):
                current_config = self.navigate(None)
            self.shared.logger.log(f"@Configurator.create_new_screen > Returned {repeat_return} times.", "TESTING")

        # handle modal display
        if current_config.get("modal"):
            self.shared.logger.log(f"@Configurator.create_new_screen > Sending modal.", "TESTING")
            await self.modal_interaction(current_config)

        # display logic -> find embed and view and display
        elif (embed := current_config.get("embed")) and current_config.get("view"):
            self.shared.logger.log(f"@Configurator.create_new_screen > Sending embed & view", "TESTING")
            await self.view.update_message(self.interaction, dict(embed=self.format_embed(embed), view=self.handle_view(current_config)))

    # if option provided exists in config, display, otherwise display FALLBACK embed - no config for that option
    async def first_screen(self) -> None:
        if current_config := self.config.get(self.option, None):
            self.local_db["local_path"].append(self.option)
            await self.view.update_message(self.interaction, {"embed": self.format_embed(self.MAIN_SCREEN), "view": self.handle_view(current_config)})
        else:
            await self.view.update_message(self.interaction, {"embed": self.format_embed(self.FALLBACK), "view": self.view.clear_items().create_back_button()})

    # handles view interaction
    async def handle_interaction(self, custom_id: str, view) -> None:
        #check for view and database
        self.shared.logger.log(f"@Configurator.handle_interaction > Got new event with ID: {custom_id}.", "TESTING")
        if not view:
            raise ValueError("No view recieved.")
        
        self.view: BaseConfigCMDView = view        
        self.interaction: discord.Interaction = self.view.interaction       
        
        if not (guild_db := self.shared.db.load_data(self.interaction.guild.id)):
            raise ValueError(f"No database data found, corrupted or missing database for: {self.interaction.guild.name} ({self.interaction.guild.id}) ?")

        # setting global values per interaction
        self.option: str = self.view.current_position
        self.guild_db: dict[str, str | dict[str, str | int] | int] = guild_db

        # start handler
        if custom_id.endswith(":START"):
            self.shared.logger.log(f"@Configurator.handle_interaction > Executed start event.", "TESTING")
            self.reset_configurator()
            await self.first_screen()

        # just switch handler
        elif custom_id.endswith(":btn_switch"):
            self.shared.logger.log(f"@Configurator.handle_interaction > Executed switch event.", "TESTING")
            self.reset_configurator()
            self.guild_db[self.option]["status"] = not self.guild_db[self.option]["status"]
            self.shared.db.save_data(self.interaction.guild.id, self.guild_db)
            await self.first_screen()

        else:
            # actual logic and resloving
            item_id: str = custom_id.split(":")[-1]
            
            # on btn_back, goes one navigation back
            if item_id == "btn_back":
                self.shared.logger.log(f"@Configurator.handle_interaction > Executed back event.", "TESTING")
                current_config: dict[str, typing.Any] = self.navigate(None)

            # handle selects
            elif item_id.startswith("slc_"):
                self.shared.logger.log(f"@Configurator.handle_interaction > Got select menu event.", "TESTING")
                first_value: str = self.interaction.data.get("values")[0]
                current_config: dict[str, typing.Any] = self.navigate(item_id, first_value)

            # handle buttons
            elif item_id.startswith("btn_"):
                self.shared.logger.log(f"@Configurator.handle_interaction > Got button event.", "TESTING")
                current_config: dict[str, typing.Any] = self.navigate(item_id)
            else:
                raise NotImplementedError("Failed to navigate interaction in the config.")

            await self.create_new_screen(current_config)
        
        self.shared.logger.log(f"@Configurator.handle_interaction > Local path: {self.local_db["local_path"]} DB path: {self.local_db["db_path"]}", "TESTING")
  
