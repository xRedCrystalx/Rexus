import discord, sys, typing
sys.dont_write_bytecode = True
from discord.ext import commands
from discord import app_commands
import src.connector as con


class SearchUserCommand(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot
        self.c: con.Colors.C | con.Colors.CNone = self.shared.colors

    @app_commands.choices(option=[
        app_commands.Choice(name="keyword equals to name", value="=="),
        app_commands.Choice(name="keyword in name", value="in")
        ],
        name=[
        app_commands.Choice(name="both", value="both"),   
        app_commands.Choice(name="display_name", value="display_name"),
        app_commands.Choice(name="global_name", value="global_name")
        ])

    @app_commands.command(name="search_user", description="Searches all people that have keyword in their name.")
    async def search_user(self, interaction: discord.Interaction, option: app_commands.Choice[str], name: app_commands.Choice[str], keyword: str) -> None:
        guild_db: dict[str, typing.Any] = self.shared.db.load_data(interaction.guild.id)
        bot_config: dict[str, typing.Any] = self.shared.db.load_data()

        def message_handeler(data: list[tuple]) -> None:
            idlen: int = 0
            namelen: int = 0
            temp: list[tuple] = []
            
            for user in data:
                if idlen >= 1000 or namelen >= 1000:
                    embed: discord.Embed=discord.Embed(title=":rotating_light: **Users Found!** :rotating_light:", description=f"Search keyword: **{keyword}**\nKick command: `?kick [UserID] Impersonating a youtuber/celebrity. Come back when you've changed your name or you can request a nickname from staff`\nPossible impostors:", color=discord.Colour.dark_embed())
                    embed.add_field(name="Names:", value=f"\n".join([x[0] for x in temp]), inline=True)
                    embed.add_field(name="Ids:", value=f"\n".join([x[1] for x in temp]), inline=True)
                    embed.set_footer(text="Wrong information or bug? Ping bot developer @xRedCrystalx#5165")
                    embeds.append(embed)

                    idlen = 0
                    namelen = 0
                    temp = []

                namelen += len(user[0])+1
                idlen += len(user[1])+1
                temp.append(user)

            if temp:
                embed: discord.Embed=discord.Embed(title=":rotating_light: **Users Found!** :rotating_light:", description=f"Search keyword: **{keyword}**\nKick command: `?kick [UserID] Impersonating a youtuber/celebrity. Come back when you've changed your name or you can request a nickname from staff`\nPossible impostors:", color=discord.Colour.dark_embed())
                embed.add_field(name="Names:", value=f"\n".join([x[0] for x in temp]), inline=True)
                embed.add_field(name="Ids:", value=f"\n".join([x[1] for x in temp]), inline=True)
                embed.set_footer(text="Wrong information or bug? Ping bot developer @xRedCrystalx#5165")
                embeds.append(embed)

        if (guild_db["ServerInfo"]["StaffRole"] in [x.id for x in interaction.user.roles]) or (interaction.user.id in [x for x in bot_config["owners"]]):
            data: list[tuple[str, int]] = []
            embeds: list[discord.Embed] = []

            for member in interaction.guild.members:
                if name.value != "both":
                    eval_code: str = f"'{keyword}'.lower() {option.value} member.{name.value}.lower()"
                    try:
                        if eval(eval_code):
                            data.append((str(getattr(member, name.value)), str(member.id)))
                    except:
                        pass
                else:
                    eval_code: str = f"'{keyword}'.lower() {option.value} member.display_name.lower() or '{keyword}' {option.value} member.global_name.lower()"
                    try:
                        if eval(eval_code):
                            data.append((str(member.display_name if eval(f"'{keyword}'.lower() {option.value} member.display_name.lower()") else member.global_name), str(member.id)))
                    except:
                        pass
            if data: 
                message_handeler(data=data)
            else:
                embed=discord.Embed(title="**No Users Found!**", description=f"No User Found or Error has occured.\nSearch keyword: **{keyword}**", color=discord.Colour.dark_embed(), timestamp=await self.CONNECTOR.callable(fun="datetime"))
                embed.set_footer(text="Wrong information or bug? Ping bot developer @xRedCrystalx")
                embeds.append(embed)

            buttonH: con.buttonHandler = await self.CONNECTOR.callable(fun="buttonHandler", timeout=5*60)
            embed=discord.Embed(title="**Searching Users...**", description=f"Checking **{interaction.guild.member_count}** members.\nSearch keyword: **{keyword}**", color=discord.Colour.dark_embed(), timestamp=await self.CONNECTOR.callable(fun="datetime"))
            embed.set_footer(text="Wrong information or bug? Ping bot developer @xRedCrystalx")

            await interaction.response.send_message(embed=embed, view=buttonH.create_paginator(messages=embeds))
            buttonH.original_message = await interaction.original_response()
        else:
            await interaction.response.send_message("You do not have permissions to execute this command.", ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    pass
    #await bot.add_cog(SearchUserCommand())


#TODO: full update