import sys, typing, discord
sys.dont_write_bytecode = True
import src.connector as con

async def fetch_invite_links(string: str, option: typing.Literal["simon", "scam_guilds"] = None) -> list[int]:
    invites: list[int] = []
    for link in con.shared.global_db["invite_links"].get("regex").findall(string):
        if link not in con.shared.global_db["invite_links"].get(option):
            try:
                invite_link: discord.Invite = await con.shared.bot.fetch_invite(link)
                invites.append(invite_link.guild.id)

                if option:
                    con.shared.global_db["invite_links"][option][link] = invite_link.guild.id
            except: continue
    return invites