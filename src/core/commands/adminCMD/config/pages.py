import sys, discord, typing, re, ast
sys.dont_write_bytecode = True
import src.connector as con
from discord import Embed

class HelpPages:
    shared: con.Shared = con.shared

    ERROR: Embed = Embed(title="Error", description="An error has occured. Please report this to the developer.\n**Error code:** `{error}`", color=discord.Colour.dark_embed(), timestamp=shared._datetime())
    ERROR.set_footer(text="Configuration has been terminated.")
    
    START: Embed = Embed(title="Configuration", description="Here, you can view, set, edit and learn about NoPing's plugins and configurations!\n**Use buttons down below to navigate.**", color=discord.Colour.dark_embed(), timestamp=shared._datetime())

    general: Embed = Embed(title="General", description="e", color=discord.Colour.dark_embed(), timestamp=shared._datetime())
    
    altDetection: Embed = Embed(title="Alt Detection", description="Alt detection is a plugin that detects new joined members and checks their account creation date.", color=discord.Colour.dark_embed(), timestamp=shared._datetime())
    altDetection.add_field(name="`` Functionality ``", value="1. <:search:1203411854336983161> Member joins the guild\n2. <:profile:1203409921719140432> Bot checks account age\n3. <:message:1203419599824101416> Bot sends log message (if age < 3 days)")
    altDetection.add_field(name="`` Future Update ``", value="Smart detection: check really young accounts after a member ban.")

    impersonatorDetection: Embed = Embed(title="Impersonator Detection", description="Impersonator Detection is a plugin that detects new joined members and member profile updates. Bot checks their display and global name for any known youtuber/company/celebrity names etc. Real accounts are ignored.", color=discord.Colour.dark_embed(), timestamp=shared._datetime())
    impersonatorDetection.add_field(name="`` Functionality ``", value="1. <:search:1203411854336983161> Member joins the guild or updates profile\n2. <:profile:1203409921719140432> Bot checks display & global names\n3. <:message:1203419599824101416> Bot sends log message (if match was found & user ID doesn't match real person)", inline=False)
    
    linkProtection: Embed = Embed(title="Link Protection", description="Link Protection is a plugin that detects new messages and tries to find link matches. Plugin logs and deletes detected messages.", color=discord.Colour.dark_embed(), timestamp=shared._datetime())
    linkProtection.add_field(name="`` Functionality ``", value="1. <:search:1203411854336983161> Member sends message\n2. <:message:1203419599824101416> Bot checks message content & tries to find link matches\n3. <:dev:1203411510832136202> Bot sends log message & deletes sender's message (if match was found & config doesn't stop it)", inline=False)
    linkProtection.add_field(name="`` Future Update ``", value="Role ignore, scam link detection, allowing giveaways/gifs, allowing social media links, only block masked links etc.", inline=False)

    pingProtection: Embed = Embed(title="Ping Protection", description="Ping Protection is a plugin that detects new messages and tries to find ping matches. If the pinged user has `MemberProtection`, `StaffProtection` or `YouTuberProtection` role, and if the message author doesn't have `BypassRole`, warns, logs and calls staff (optional). Bots are already build-in in the system.", color=discord.Colour.dark_embed(), timestamp=shared._datetime())
    pingProtection.add_field(name="`` Functionality ``", value="1. <:search:1203411854336983161> Member sends message\n2. <:message:1203419599824101416> Bot checks message content & tries to find ping matches\n3. <:dev:1203411510832136202> Bot sends warn & log message AND what was set in configuration (if match was found & user doesn't have bypass role)", inline=False)
    pingProtection.add_field(name="`` Future Update ``", value="Fully customizable detections.", inline=False)

    autoDelete: Embed = Embed(title="Auto Delete", description="AutoDelete is a plugin that deletes new created messages after x seconds/minutes/hours (depending of configuration) in the channel.", color=discord.Colour.dark_embed(), timestamp=shared._datetime())
    autoDelete.add_field(name="`` Functionality ``", value="1. <:search:1203411854336983161> Member sends message\n2. <:settings:1205253280741982259> Bot saves message & waits x seconds (configured time)\n3. <:delete:1205252465252114452> Bot tries to delete message.", inline=False)

    autoSlowmode: Embed = Embed(title="Auto Slowmode", description="AutoSlowmode is a plugin that records messages every 5 minutes and determinates how active channel is. Automatically sets slowmode to different values (seconds).", color=discord.Colour.dark_embed(), timestamp=shared._datetime())
    autoSlowmode.add_field(name="`` Functionality ``", value="1. <:search:1203411854336983161> Members send message\n2. <:log:1203410684365504692> Bot counts messages in specified channels\n3. <:dev:1203411510832136202> Every 5 minutes, bot calculates activity\n4. <:settings:1205253280741982259> Edits channel's slowmode delay", inline=False)
    autoSlowmode.add_field(name="`` Future Update ``", value="Better algorithm to detect actual number of active members, messages/members etc.", inline=False)

    automod: Embed = Embed(title="Automod Responses", description="Automod Responses is a plugin that sends custom message under Automod's trigger message. Normally used for automatically creating warn/ban/kick commands for other bots, for example Dyno, MEE6, Probot...\nTo use placeholders, use `{...}` *Example: ?warn {user.id} Spamming*", color=discord.Colour.dark_embed(), timestamp=shared._datetime())
    automod.add_field(name="Placeholder user:", value="This placeholder specifies the __guild member__ who triggerd Automod.\n- `user.name` ➔ Get username of targeted member\n- `user.id` ➔ Get user ID of targeted member\n- `user.mention` ➔ Mentions triggered member", inline= True)
    automod.add_field(name="Placeholder channel:", value="This placeholder specifies the __channel__ where member triggered Automod.\n- `channel.name` ➔ Get channel name\n- `channel.id` ➔ Get channel ID\n- `channel.mention` ➔ Mentions channel", inline=True)
    automod.add_field(name="`` Functionality ``", value="1. <:search:1203411854336983161> Automod triggers\n2. <:settings:1205253280741982259> Bot reads report and attempts to find correct response message\n3. <:message:1203419599824101416> Formats and sends message under automod's report", inline=False)

    AI: Embed = Embed(title="Artificial Intelligence", description="Artificial Inteligence (computer that understands human text and responds to it). Talk to NoPing!\n**Prefix:** `> ` (space)", color=discord.Colour.dark_embed(), timestamp=shared._datetime())

    commands: Embed = Embed(title="Commands", color=discord.Colour.dark_embed(), timestamp=shared._datetime())
    commands.add_field(name="Staff Commands:", value="- `/report message_link:[Link]` Optional: `extra:[Text]`, `age:[Number]`\
                                            \n> ➔ Reports user to discord's moderation team.\
                                            \n- `/slowmode set:[Number]` Optional: `channel:[Channel]`\
                                            \n> ➔ Sets channel slowmode. If no channel specified, changes slowmode in the channel where command was executed in.\
                                            \n- `/search_user option:[Choose] name:[Choose] keyword:[Text]`\
                                            \n> ➔ Searches for possible names with the given keyword/phrase and shows the IDs.", inline=False)

class ConfigPages:
    shared: con.Shared = con.shared

    general: Embed = Embed(title="General", description="General settings", color=discord.Colour.dark_embed(), timestamp=shared._datetime())

    linkProtection: Embed = Embed(title="Link Protection", description="**Status:** {status:_boolTrans}\n**Logging Channel:** {log_channel:resolve_id?var='mention'}", color=discord.Colour.dark_embed(), timestamp=shared._datetime())
    #linkProtection.add_field(name="Options", value="**Allow Discord Invites:** `{options[allowDiscordInvites]}`\n**Allow Social Links:** `{options[allowSocialLinks]}`\n**Allow Nitro Gifts:** `{options[allowNitroGifts]}`")

    pingProtection: Embed = Embed(title="Ping Protection", description="**Status:** {status:_boolTrans}\n**Bypass Role:** {bypassRole:resolve_id?var='mention'}\n**Detect Reply Pings:** {detectReplyPings:to_code}\n**Ignored Channels:** {ignoredChannels:resolve_id?var='mention'&handle_list_format?sep='point'}", color=discord.Colour.dark_embed(), timestamp=shared._datetime())
    pingProtection.add_field(name="rules $ ``  {key}  ``", value="**Protected role:** {role:resolve_id?var='mention'}\n**Ping staff:** {ping:to_code}\n**Log message:** {log:to_code}\n**Logging channel:** {logChannel:resolve_id?var='mention'}\n**Delete message:** {delete:to_code}", inline=False)

    automod: Embed = Embed(title="AutoMod Response", description="Under development.\nUse `/automod load_rules` and `/automod create_response` commands.", color=discord.Colour.dark_embed(), timestamp=shared._datetime())

    autoDelete: Embed = Embed(title="Auto Delete", description="**Status:** {status:_boolTrans}\n**Logging Channel:** {log_channel:resolve_id?var='mention'}\n**Monitored channels:**\n{monitored:resolve_id?var='mention'&handle_list_format?sep='point'}", color=discord.Colour.dark_embed(), timestamp=shared._datetime())

    autoSlowmode: Embed = Embed(title="Auto Slowmode", description="**Status:** {status:_boolTrans}\n**Monitored channels:**\n{monitored:resolve_id?var='mention'|time&to_code>handle_list_format?sep='point'}", color=discord.Colour.dark_embed(), timestamp=shared._datetime())

    AI: Embed = Embed(title="Artificial intelligence", description="**Status:** {status:_boolTrans}\n**Respond Channels:**\n{talkChannels:resolve_id?var='mention'&handle_list_format?sep='point'}", color=discord.Colour.dark_embed(), timestamp=shared._datetime())

    commands: Embed = Embed(title="Commands", description="e", color=discord.Colour.dark_embed(), timestamp=shared._datetime())


    def _boolTrans(self, boolean: bool)-> str:
        return "`Enabled`" if boolean else "`Disabled`"

    def _idTrans(self, id: int, option: typing.Literal["channel", "role", "member"]) -> str:
        return "`None`" if id is None else f"<#{id}>" if option == "channel" else f"<@&{id}>" if option == "role" else f"<@!{id}>" if option == "user" else "Error"

    def resolve_id(self, id: int | str | list, interaction: discord.Interaction = None, var: str = None) -> discord.abc.GuildChannel | discord.User | discord.Member | discord.Role | list:
        def obj(ID: int) -> object:
            try:
                if channel := guild.get_channel(ID):
                    return channel
                elif role := guild.get_role(ID):
                    return role
                elif member := guild.get_member(ID):
                    return member
            except Exception as error:
                self.shared.logger.log( f"@ConfigPages.resolve_id.obj > {type(error).__name__}: {error}", "ERROR")

        try:
            if not interaction:
                interaction = self.interaction

            if guild := interaction.guild:
                if isinstance(id, (tuple, list)):
                    if not var:
                        return [obj(int(x)) for x in id]
                    else:
                        return [getattr(obj(int(x)), var) for x in id]
                else:
                    if not var:
                        return obj(int(id))
                    else:
                        return getattr(obj(int(id)), var)

        except ValueError:
            return id
        except Exception as error:
            self.shared.logger.log( f"@ConfigPages.resolve_id > {type(error).__name__}: {error}", "ERROR")

    def handle_list_format(self, value: list, sep: typing.Literal["comma", "point"]) -> str | None:
        try:
            if isinstance(value, (tuple, list)):
                if sep == "comma":
                    return ", ".join(map(str, value))
                elif sep == "point":
                    return "\n".join([f"- {item}" for item in value])
                else:
                    return ", ".join(map(str, value))
        except Exception as error:
            self.shared.logger.log( f"@ConfigPages.handle_list_format > {type(error).__name__}: {error}", "ERROR")
        return None
    
    def to_code(self, var) -> str:
        if isinstance(var, (tuple, list)):
            return [f"`{x}`" for x in var]
        else:
            return f"`{var}`"
    
    def time(self, time: int) -> str:
        return time

    def format(self, string: str, **kwargs) -> str:
        def handle_functions(value: str, funcs: str) -> typing.Any:
            try:
                functions: list[list[str, dict[str, typing.Any]]] = []

                for func in funcs.split("&"):
                    if len(data := func.split("?")) <= 1:
                        functions.append([data[0].strip(), {}])
                    else:
                        params = map(str.strip, data[1].split(","))
                        kwargs: dict[str, typing.Any] = {k: ast.literal_eval(v) for k, v in (param.split("=") for param in params)}
                        functions.append([data[0].strip(), kwargs])

                for function, arguments in functions:                
                    callable: typing.Callable = getattr(self, function)
                    value = callable(value, **arguments)
                return value
            except Exception as error:
                self.shared.logger.log(f"@ConfigPages.format.handle_functions > {type(error).__name__}: {error}", "ERROR")
            return None
        
        try:
            placeholders: list[str] = re.findall(r"\{([^:}]+)(?::([^}]+))?\}", string)

            for value_path, funcs in placeholders:
                value_path, funcs = (value_path.strip(), funcs.strip())
                
                if funcs == "":
                    placeholder: str = "{"+value_path+"}"
                    string = string.replace(placeholder, placeholder.format(**kwargs))
                else:
                    placeholder: str = "{"+f"{value_path}:{funcs}"+"}"
                    try:
                        value: str =  ast.literal_eval(("{"+value_path+"}").format(**kwargs))
                    except:
                        value: str = ("{"+value_path+"}").format(**kwargs)
                    
                    if isinstance(value, dict):
                        keys = tuple(value.keys())
                        values = tuple(value.values())

                        functions: list[str] = funcs.split("|") if "|" in funcs else [funcs] # 1 or 2
                        final: str | None = functions[-1].split(">")[-1] if ">" in funcs else None

                        formatted_keys: str | list[str]= handle_functions(keys, functions[0]) if keys and functions[0] != "" else keys
                        formatted_values: str | list[str] = handle_functions(values, functions[-1].split(">")[0]) if values and len(functions) == 2 and functions[-1] != "" else values

                        formatted: list[str] = [f"{key}: `{formatted_values[index]}`" for index, key in enumerate(formatted_keys)]
                        
                        if final:
                            formatted = handle_functions(formatted, final)

                        string = string.replace(placeholder, str(formatted))
                    
                    else:
                        string = string.replace(placeholder, str(handle_functions(value, funcs)))
            return string

        except Exception as error:
            self.shared.logger.log( f"@ConfigPages.format > {type(error).__name__}: {error}", "ERROR")
        return None

    def handle_fields(self, sample, data: dict[str, dict[str, str]]) -> list[dict[str, str | bool]]:
        config, sample_name = str(sample.name).split("$", 1)
        sample.name = sample_name

        for path in config.strip().split("."):
            data = data[path]

        fields: list = []

        for key, value in data.items():
            fields.append({
                "name" : self.format(sample.name, key=key, **value),
                "value" : self.format(sample.value, key=key, **value),
                "inline" : sample.inline
            })
        return fields or []

    def create_embed(self, data: dict, embed: discord.Embed, interaction: discord.Interaction, name: str) -> discord.Embed:
        self.interaction: discord.Interaction = interaction
        
        if not embed:
            embed: Embed = Embed(title=name, description=f"**Status:** `{self._boolTrans(data.get("status"))}`\n**Logging channel:** {self._idTrans(data.get("log_channel"), "channel")}", color=discord.Colour.dark_embed(), timestamp=self.shared._datetime())

        embed.description = self.format(embed.description, **data)

        for field in embed.fields.copy():
            index: int = embed.fields.index(field)
            if "$" in field.name:
                for new_filed in self.handle_fields(field, data):
                    embed.add_field(name=new_filed["name"], value=new_filed["value"], inline=new_filed["inline"])
                embed.remove_field(index)
            else:
                embed.set_field_at(index, name=self.format(field.name, **data), value=self.format(field.value, **data), inline=field.inline)
        return embed

