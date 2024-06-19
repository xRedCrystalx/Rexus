import sys
sys.dont_write_bytecode = True

SEPERATOR: str = "┇"

class CustomEmoji:
    PING: str = "<:ping:1226194531528216727>"           # @ - ping, mention, at symbol
    LOCATION: str = "<:location:1226157748547227668>"   # location (channel, guild), language, world location
    ROLE: str = "<:role:1226153759722438707>"           # role
    BOT: str = "<:bot:1226153730836140054>"             # bot, self, switch
    SETTINGS: str = "<:settings:1205253280741982259>"   # settings, gear, configuration
    DELETE: str = "<:delete:1205252465252114452>"       # bin - delete, remove
    TEXT_C: str = "<:text_c:1203423388320669716>"       # hash - text channel, hash tag
    MSG_ID: str = "<:msg_id:1203422168046768129>"       # message ID
    MESSAGE: str = "<:message:1203419599824101416>"     # bubble - message, chatting, thinking
    SECURITY: str = "<:security:1203412011271069808>"   # server, security, protected
    VERIFIED: str = "<:verified:1203411997375467570>"   # --future--
    PARTNER: str = "<:partner:1203411978354303098>"     # --future--
    SEARCH: str = "<:search:1203411854336983161>"       # search, looking, finding
    LINK: str = "<:link:1203411766005207121>"           # link, URL
    MAIL: str = "<:mail:1203411749462867999>"           # --future--
    MEMBER: str = "<:member:1203411735210365059>"       # member, hi, user, human
    ADMIN: str = "<:admin:1203411632361971724>"         # admin, server admin
    CHART: str = "<:chart:1203411532504109056>"         # statistics
    DEV: str = "<:dev:1203411510832136202>"             # developer, in development, working on
    LOG: str = "<:log:1203410684365504692>"             # log, logging, log_setting
    GLOBAL: str = "<:global:1203410626492240023>"       # global, global_name
    RULES: str = "<:rules:1203410571140137050>"         # rules, rule_channel
    ART: str = "<:art:1203410471042945095>"             # --future--
    MODERATOR: str = "<:moderator:1203410451690426388>" # mod, staff, server protection
    ID: str = "<:ID:1203410054016139335>"               # ID, identificator
    PROFILE: str = "<:profile:1203409921719140432>"     # profile, card, user_profile
    SLASH: str = "<:slash:1253025358890926142>"         # command, slash command

class EmojiImage:
    PING: str = "https://i.ibb.co/sq2sTff/ping.png"
    LOCATION: str = ""
    ROLE: str = ""
    BOT: str = "https://i.ibb.co/Yb1QH1V/bot.png"
    SETTINGS: str = ""
    DELETE: str = "https://i.ibb.co/5kP5pNK/delete.png"
    TEXT_C: str = ""
    MSG_ID: str = ""
    MESSAGE: str = "https://i.ibb.co/kDZZMVP/message.png"
    SECURITY: str = "https://i.ibb.co/3dV35Hp/security.png"
    VERIFIED: str = ""
    PARTNER: str = ""
    SEARCH: str = ""
    LINK: str = ""
    MAIL: str = ""
    MEMBER: str = "https://i.ibb.co/R6WZm04/member.png"
    ADMIN: str = ""
    CHART: str = ""
    DEV: str = ""
    LOG: str = ""
    GLOBAL: str = ""
    RULES: str = ""
    ART: str = ""
    MODERATOR: str = ""
    ID: str = ""
    PROFILE: str = ""
    SLASH: str = "https://i.ibb.co/nQFfH71/slash-command.png"