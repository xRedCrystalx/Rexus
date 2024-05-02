import sys, discord
sys.dont_write_bytecode = True
import src.connector as con
from discord import Embed

class HelpPages:
    def __init__(self, guild_id: int) -> None:
        self.guild_id: int = guild_id

    shared: con.Shared = con.shared

    ERROR: Embed = Embed(title="Error", description="An error has occured. Please report this to the developer.\n**Error code:** `{error}`", color=discord.Colour.dark_embed(), timestamp=shared.time.datetime())
    ERROR.set_footer(text="Configuration has been terminated.")
    
    START: Embed = Embed(title="Configuration", description="Here, you can view, set, edit and learn about NoPing's plugins and configurations!\n**Use buttons down below to navigate.**", color=discord.Colour.dark_embed(), timestamp=shared.time.datetime())

    # link github, youtube etc. - invite link - website 
    general: Embed = Embed(title="General", description=f"Hey there!\nI'm **NoPing**, friendly little robot that will help you with server protection!\n\nHere are some important commands:\n- </config:1221521894713589771> ➔ Command to configure me\n- </noping:1224009186531217478> ➔ Command for other information about me\n\nHelp me reach **100 guilds** by recommending me to your friends, so we can together get me verified! Here is the [invite link](https://discord.com/oauth2/authorize?client_id=980031906836009000).\nThank you :)", color=discord.Colour.dark_embed(), timestamp=shared.time.datetime())
    general.add_field(name="`` Info ``", value=f"- **Developer:** `@xRedCrystalx`\n- **Version:** `3.0.0`\n- **Ping:** `{round(shared.bot.latency * 1000, 0)}ms`\n- **Shards:** `{shared.bot.shard_count}`\n- **Guild count:** {len(shared.bot.guilds)}")
    general.add_field(name="`` Links ``", value="- [`Support Server`](https://discord.gg/gzx3kxu68x)\n- [`YouTube`](https://www.youtube.com/channel/UCYQ7OuJL8ceDbKqBG_PWdgQ)\n- [`Twitter/X`](https://twitter.com/xRedCrystal)\n- [`Github`](https://github.com/xRedCrystalx)")
    general.set_footer(text="Private & important matter: xredcrystaledx@gmail.com")

    cmd: Embed = Embed(title="Commands", color=discord.Colour.dark_embed(), timestamp=shared.time.datetime())
    cmd.add_field(name="Staff Commands:", value="- `/slowmode set:[Number]` Optional: `channel:[Channel]`\
                                            \n> ➔ Sets channel slowmode. If no channel specified, changes slowmode in the channel where command was executed in.\
                                            \n- `/purge user:[Member]` Optional: `number:[Number]`\
                                            \n> ➔ Checks **[number] (default 100)** messages in each channel and deletes messages of that user.", inline=False)
    
    alt: Embed = Embed(title="Alt Detection", description="Alt detection is a plugin that detects new joined members and checks their account creation date.", color=discord.Colour.dark_embed(), timestamp=shared.time.datetime())
    alt.add_field(name="`` Functionality ``", value="1. <:search:1203411854336983161> Member joins the guild\n2. <:profile:1203409921719140432> Bot checks account age\n3. <:message:1203419599824101416> Bot sends log message (if age < 3 days)")
    alt.add_field(name="`` Future Update ``", value="Smart detection: check really young accounts after a member ban.")

    imper: Embed = Embed(title="Impersonator Detection", description="Impersonator Detection is a plugin that detects new joined members and member profile updates. Bot checks their display and global name for any known youtuber/company/celebrity names etc. Real accounts are ignored.", color=discord.Colour.dark_embed(), timestamp=shared.time.datetime())
    imper.add_field(name="`` Functionality ``", value="1. <:search:1203411854336983161> Member joins the guild or updates profile\n2. <:profile:1203409921719140432> Bot checks display & global names\n3. <:message:1203419599824101416> Bot sends log message (if match was found & user ID doesn't match real person)", inline=False)
    
    ai: Embed = Embed(title="Artificial Intelligence", description="Artificial Inteligence (computer that understands human text and responds to it). Talk to NoPing!\n**Prefix:** `> ` (space)", color=discord.Colour.dark_embed(), timestamp=shared.time.datetime())

    automod: Embed = Embed(title="Automod Responses", description="Automod Responses is a plugin that sends custom message under Automod's trigger message. Normally used for automatically creating warn/ban/kick commands for other bots, for example Dyno, MEE6, Probot...\nTo use placeholders, use `{...}` *Example: ?warn {user.id} Spamming*", color=discord.Colour.dark_embed(), timestamp=shared.time.datetime())
    automod.add_field(name="Placeholder user:", value="This placeholder specifies the __guild member__ who triggerd Automod.\n- `user.name` ➔ Get username of targeted member\n- `user.id` ➔ Get user ID of targeted member\n- `user.mention` ➔ Mentions triggered member", inline= True)
    automod.add_field(name="Placeholder channel:", value="This placeholder specifies the __channel__ where member triggered Automod.\n- `channel.name` ➔ Get channel name\n- `channel.id` ➔ Get channel ID\n- `channel.mention` ➔ Mentions channel", inline=True)
    automod.add_field(name="`` Functionality ``", value="1. <:search:1203411854336983161> Automod triggers\n2. <:settings:1205253280741982259> Bot reads report and attempts to find correct response message\n3. <:message:1203419599824101416> Formats and sends message under automod's report", inline=False)

    link: Embed = Embed(title="Link Protection", description="Link Protection is a plugin that detects new messages and tries to find link matches. Plugin logs and deletes detected messages.", color=discord.Colour.dark_embed(), timestamp=shared.time.datetime())
    link.add_field(name="`` Functionality ``", value="1. <:search:1203411854336983161> Member sends message\n2. <:message:1203419599824101416> Bot checks message content & tries to find link matches\n3. <:dev:1203411510832136202> Bot sends log message & deletes sender's message (if match was found & config doesn't stop it)", inline=False)
    link.add_field(name="`` Future Update ``", value="Role ignore, scam link detection, only block masked links etc.", inline=False)

    ping: Embed = Embed(title="Ping Protection", description="Ping Protection is a plugin that detects new messages and tries to find ping matches. If rule was broken and user doesn't have `BypassRole`, warns, logs and calls staff (optional).", color=discord.Colour.dark_embed(), timestamp=shared.time.datetime())
    ping.add_field(name="`` Functionality ``", value="1. <:search:1203411854336983161> Member sends message\n2. <:message:1203419599824101416> Bot checks message content & tries to find ping matches\n3. <:dev:1203411510832136202> Bot sends warn & log message AND what was set in configuration (if match was found & user doesn't have bypass role)", inline=False)

    auto_delete: Embed = Embed(title="Auto Delete", description="AutoDelete is a plugin that deletes new created messages after x seconds/minutes/hours (depending of configuration) for the channel.", color=discord.Colour.dark_embed(), timestamp=shared.time.datetime())
    auto_delete.add_field(name="`` Functionality ``", value="1. <:search:1203411854336983161> Member sends message\n2. <:settings:1205253280741982259> Bot saves message & waits x seconds (configured time_converter)\n3. <:delete:1205252465252114452> Bot tries to delete message.", inline=False)

    auto_slowmode: Embed = Embed(title="Auto Slowmode", description="AutoSlowmode is a plugin that records messages every 5 minutes and determinates how active channel is. Automatically sets slowmode to different values (seconds).", color=discord.Colour.dark_embed(), timestamp=shared.time.datetime())
    auto_slowmode.add_field(name="`` Functionality ``", value="1. <:search:1203411854336983161> Members send message\n2. <:log:1203410684365504692> Bot counts messages in specified channels\n3. <:dev:1203411510832136202> Every 5 minutes, bot calculates activity\n4. <:settings:1205253280741982259> Edits channel's slowmode delay", inline=False)
    auto_slowmode.add_field(name="`` Future Update ``", value="Better algorithm to detect actual number of active members, messages/members etc.", inline=False)

    QOFTD: Embed = Embed(title="Question of the Day", description="This plugin posts a random question every day at midnight UTC.", color=discord.Colour.dark_embed())
    QOFTD.add_field(name="`` Functionality ``", value="1. <:search:1203411854336983161> Waits for midnight in UTC\n2. <:message:1203419599824101416> Sends a random message in every channel.", inline=False)

    reaction: Embed = Embed(title="Reaction Filter", description="Reaction filter is a plugin that looks for a specific reactions and removes them. If a member continuously tries to add those reactions, bot reaction bans that member (if the role is provided in the config).", color=discord.Colour.dark_embed())
    reaction.add_field(name="`` Functionality ``", value="1. <:search:1203411854336983161> Waits for naughty reactions\n2. <:delete:1205252465252114452> Removes reactions from the message\n 3. <:message:1203419599824101416> Sends report to log channel (if provided).\n4. <:role:1226153759722438707> Multiple bad reactions by the same member -> reaction ban", inline=False)


class ConfigPages:
    def __init__(self, guild_id: int) -> None:
        self.guild_id: int = guild_id

    shared: con.Shared = con.shared
    formatter = shared.string_formats

    general: Embed = Embed(title="General", description="<:bot:1226153730836140054>┇{status:boolean_format?option='switch'&discord_format}\n<:location:1226157748547227668>┇{language:discord_format}\n<:settings:1205253280741982259> **Can admins configure?:** {allowAdminEditing:boolean_format?option='y/n'&discord_format}", color=discord.Colour.dark_embed())
    general.add_field(name="`` Admin ``", value="<:role:1226153759722438707>┇{adminRole:id_format?option='role'}\n<:text_c:1203423388320669716>┇{adminChannel:id_format?option='channel'}", inline=True)
    general.add_field(name="`` Staff ``", value="<:role:1226153759722438707>┇{staffRole:id_format?option='role'}\n<:text_c:1203423388320669716>┇{staffChannel:id_format?option='channel'}", inline=True)
    general.set_thumbnail(url="https://i.ibb.co/3dV35Hp/security.png")
    general.set_footer(text="Click on ❔ for general information about bot.")

    cmd: Embed = Embed(title="Commands", description="", color=discord.Colour.dark_embed())
    cmd.add_field(name="`` Logging ``", value="<:settings:1205253280741982259> **Log CMD execution:** {logCmdExecution:boolean_format?option='y/n'&discord_format}\n<:settings:1205253280741982259> **Log failed CMD:** {failedCmdExecution:boolean_format?option='y/n'&discord_format}\n<:text_c:1203423388320669716>┇{cmdExecutionLogChannel:id_format?option='channel'}\n__**Under development.**__")
    cmd.set_thumbnail(url="https://i.ibb.co/nQFfH71/slash-command.png")

    alt: Embed = Embed(title="Alt Detection", description="<:bot:1226153730836140054>┇{status:boolean_format?option='switch'&discord_format}\n<:text_c:1203423388320669716>┇{log_channel:id_format?option='channel'}", color=discord.Colour.dark_embed())
    alt.set_thumbnail(url="https://i.ibb.co/R6WZm04/member.png")
    
    imper: Embed = Embed(title="Impersonator Detection", description="<:bot:1226153730836140054>┇{status:boolean_format?option='switch'&discord_format}\n<:text_c:1203423388320669716>┇{log_channel:id_format?option='channel'}", color=discord.Colour.dark_embed())
    imper.set_thumbnail(url="https://i.ibb.co/R6WZm04/member.png")

    ai: Embed = Embed(title="Artificial intelligence", description="<:bot:1226153730836140054>┇{status:boolean_format?option='switch'&discord_format}", color=discord.Colour.dark_embed())
    ai.add_field(name="`` Respond Channels ``", value="{talkChannels:id_format?option='channel'&list_format}")
    ai.set_thumbnail(url="https://i.ibb.co/Yb1QH1V/bot.png")
    
    automod: Embed = Embed(title="AutoMod Response", description="Under development.\nUse **</automod load_rules:1160680000970821645>** and **</automod create_response:1160680000970821645>** commands.", color=discord.Colour.dark_embed())

    link: Embed = Embed(title="Link Protection", description="<:bot:1226153730836140054>┇{status:boolean_format?option='switch'&discord_format}\n<:text_c:1203423388320669716>┇{log_channel:id_format?option='channel'}", color=discord.Colour.dark_embed())
    link.add_field(name="`` Options ``", value="**<:settings:1205253280741982259> Allow Discord Invites:** `{options[allowDiscordInvites]:boolean_format?option='y/n'&discord_format}`\n**<:settings:1205253280741982259> Allow Social Links:** `{options[allowSocialLinks]:boolean_format?option='y/n'&discord_format}`\n<:settings:1205253280741982259> **Allow Nitro Gifts:** `{options[allowNitroGifts]:boolean_format?option='y/n'&discord_format}`")
    link.set_thumbnail(url="https://i.ibb.co/kDZZMVP/message.png")

    ping: Embed = Embed(title="Ping Protection", description="<:bot:1226153730836140054>┇{status:boolean_format?option='switch'&discord_format}\n<:settings:1205253280741982259> **Detect Reply Pings:** {detectReplyPings:boolean_format?option='y/n'&discord_format}\n<:settings:1205253280741982259> **Ignored Channels:**\n{ignoredChannels:id_format?option='channel'&list_format}", color=discord.Colour.dark_embed())
    ping.add_field(name="rules $ ``  {key}  ``", value="<:role:1226153759722438707>┇{role:id_format?option='role'}\n<:role:1226153759722438707>┇{bypass:id_format?option='role'}\n<:ping:1226194531528216727>┇{ping:boolean_format?option='y/n'&discord_format}\n<:log:1203410684365504692>┇{log:boolean_format?option='y/n'&discord_format}\n<:text_c:1203423388320669716>┇{logChannel:id_format?option='channel'}\n<:delete:1205252465252114452>┇{delete:boolean_format?option='y/n'&discord_format}", inline=False)
    ping.set_thumbnail(url="https://i.ibb.co/sq2sTff/ping.png")

    auto_delete: Embed = Embed(title="Auto Delete", description="<:bot:1226153730836140054>┇{status:boolean_format?option='switch'&discord_format}", color=discord.Colour.dark_embed())
    auto_delete.add_field(name="`` Monitored channels ``", value="{monitored:id_format?option='channel'|time_converter&discord_format>list_format}")
    auto_delete.set_thumbnail(url="https://i.ibb.co/5kP5pNK/delete.png")

    auto_slowmode: Embed = Embed(title="Auto Slowmode", description="<:bot:1226153730836140054>┇{status:boolean_format?option='switch'&discord_format}", color=discord.Colour.dark_embed())
    auto_slowmode.add_field(name="`` Monitored channels ``", value="{monitored:id_format?option='channel'|time_converter&discord_format>list_format}")
    auto_slowmode.set_thumbnail(url="https://i.ibb.co/kDZZMVP/message.png")

    QOFTD: Embed = Embed(title="Question of the Day", description="<:bot:1226153730836140054>┇{status:boolean_format?option='switch'&discord_format}", color=discord.Colour.dark_embed())
    QOFTD.add_field(name="`` Watched ``", value="{watched:id_format?option='channel'&list_format}")
    QOFTD.set_thumbnail(url="https://i.ibb.co/kDZZMVP/message.png")

    reaction: Embed = Embed(title="Reaction Filter", description="<:bot:1226153730836140054>┇{status:boolean_format?option='switch'&discord_format}\n<:text_c:1203423388320669716>┇{log_channel:id_format?option='channel'}\n<:role:1226153759722438707>┇{reactionBanRole:id_format?option='role'}", color=discord.Colour.dark_embed())
    reaction.set_thumbnail(url="https://i.ibb.co/3dV35Hp/security.png")

    def handle_fields(self, sample: Embed, data: dict[str, dict[str, str]]) -> list[dict[str, str | bool]] | list:
        config, sample_name = str(sample.name).split("$", 1)
        sample.name = sample_name

        for path in config.strip().split("."):
            data = data[path]

        fields: list = []

        for key, value in data.items():
            fields.append({
                "name" : self.formatter.format(sample.name, {"key": key, **value}),
                "value" : self.formatter.format(sample.value, {"key": key, **value}),
                "inline" : sample.inline
            })
        return fields or []

    def create_embed(self, data: dict, blueprint_embed: discord.Embed | None, interaction: discord.Interaction, name: str) -> discord.Embed:
        self.interaction: discord.Interaction = interaction

        if blueprint_embed:
            embed: Embed = Embed(title=blueprint_embed.title or "", description=self.formatter.format(blueprint_embed.description or "", data), color=blueprint_embed.color, timestamp=self.shared.time.datetime())
            
            if blueprint_embed.thumbnail.url:
                self.shared.logger.log(f"@ConfigPages.create_embed > Blueprint has thumbnail: {blueprint_embed.thumbnail.url}", "NP_DEBUG")
                embed.set_thumbnail(url=blueprint_embed.thumbnail.url)
            
            if blueprint_embed.footer.text:
                embed.set_footer(text=blueprint_embed.footer.text)

            self.shared.logger.log(f"@ConfigPages.create_embed > Creating new {name} embed.", "NP_DEBUG")

            if blueprint_embed and blueprint_embed.fields:
                self.shared.logger.log(f"@ConfigPages.create_embed > Handling fields", "NP_DEBUG")
                for field in blueprint_embed.fields.copy():
                    if "$" in field.name:
                        for new_filed in self.handle_fields(field, data):
                            embed.add_field(name=new_filed["name"], value=new_filed["value"], inline=new_filed["inline"])
                    else:
                        embed.add_field(name=self.formatter.format(field.name, data), value=self.formatter.format(field.value, data), inline=field.inline)
        else:
            embed: Embed = Embed(title=name, description=f"<:bot:1226153730836140054>┇`{self.formatter.boolean_format(data.get("status"), option="switch")}`\n<:text_c:1203423388320669716>┇{self.formatter.id_format(data.get("log_channel"), "channel")}", color=discord.Colour.dark_embed(), timestamp=self.shared.time.datetime())
        return embed
