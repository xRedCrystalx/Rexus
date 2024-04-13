import sys, discord
sys.dont_write_bytecode = True
import connector as syscon

class AchievementSystem:
    def __init__(self) -> None:
        self.CONNECTOR: syscon.SysConnector = syscon.sys_connector
        self.bot: syscon.commands.Bot = self.CONNECTOR.bot
        
    async def give_achievement(self, guild_id: int, member_id: int) -> None:
        ServerData: dict = self.CONNECTOR.database.load_data(server_id=guild_id, serverData=True)
        if ServerData["Plugins"]["Achievements"] and ServerData["LevelingSystem"]["config"]["achievements"] != {}:
            achievements: dict[str, dict[str, dict[str, int] | str]] = ServerData["LevelingSystem"]["config"]["achievements"]
            member_data: dict[str, dict[str, int | list[int]]] = ServerData["LevelingSystem"][str(member_id)]
            
            for achievement_id, achievement_data in achievements.items():
                if achievement_id not in member_data["achievements"]:
                    check: list[bool] = []
                    for requirement_type, requirement in achievement_data["requirements"].items():
                        data: dict[str, dict[str, int | list[int]]] = member_data
                        for path in requirement_type.split(".")[:-1]:
                            data = data[path]
                        
                        if data[requirement_type.split('.')[-1]] >= requirement:
                            check.append(True)
                        else:
                            check.append(False)
                    
                    if False not in check:
                        if ServerData["Logging"]["Achievements"]:
                            try:
                                log_channel: discord.TextChannel = self.bot.get_channel(ServerData["Logging"]["Achievements"])
                                guild: discord.Guild = self.bot.get_guild(guild_id)
                                member: discord.Member = guild.get_member(member_id)
                                
                                embed: discord.Embed = discord.Embed(title="Achievement Acquired!", description=f"**{member.display_name}** has successfully acquired **{achievement_data['name']}** achievement.\n**Congratulations!**", color=discord.Colour.dark_embed(), timestamp=await self.CONNECTOR.callable(fun="datetime"))
                                embed.set_thumbnail(url=member.display_avatar.url)
                                await log_channel.send(embed=embed)

                            except Exception as error:
                                await self.CONNECTOR.logging(logType="ERROR", data=f"Failed to send achievement give message. {type(error).__name__}: {error}")
                        
                        member_data["achievements"].append(achievement_id)
                        
                        for reward_type, reward in achievement_data["rewards"].items():
                            data = member_data
                            for path in reward_type.split(".")[:-1]:
                                data = data[path]
                            
                            data[reward_type.split('.')[-1]] += reward
                        
            self.CONNECTOR.database.save_data(server_id=guild_id, update_data=ServerData)