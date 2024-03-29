import discord, sys, typing, asyncio
sys.dont_write_bytecode = True
from discord.ext import commands
import connector as syscon


class LevelingSystem:
    def __init__(self) -> None:
        self.CONNECTOR: syscon.SysConnector = syscon.sys_connector
        self.bot: commands.Bot = self.CONNECTOR.bot

        self.voice_xp_amount: float = 0.5
        self.reaction_xp_amount: int = 5
        self.giveaway_xp_amount_min, self.giveaway_xp_amount_max = (80, 200)

        self.db_instance: dict[str, dict[str, int]] = {
            "levels": {
                "message" : 0,
                "voice": 0,
                "reaction" : 0, 
                "giveaways" : 0,
                }, 
            "message" : {
                "counter" : 0, 
                "xp" : 0, 
                "global_xp" : 0,
                "rewards" : []
                }, 
            "reaction" : {
                "counter" : 0, 
                "xp" : 0, 
                "global_xp" : 0,
                "rewards" : []
                },
            "giveaway" : {
                "counter" : 0, 
                "xp" : 0, 
                "global_xp" : 0,
                "rewards" : []
                },
            "voice" : {
                "time" : 0,
                "xp" : 0,
                "global_xp" : 0,
                "rewards" : []
                },
            "GLOBAL" : {
                "level" : 0,
                "global_xp" : 0,
                "xp" : 0,
                "contribution" : {
                    "message" : 0,
                    "voice" : 0,
                    "reaction" : 0,
                    "giveaway" : 0
                },
                "rewards" : []
            },
            "achievements" : []
        }
        
        self.output: list = []
        self.bot.loop.create_task(self.sender())

    async def calculate(self, current_xp: int, current_lvl: int) -> tuple[int, ...]:
        while True:
            xp_required: int = await self.CONNECTOR.callable(fun="calc_xp", level=current_lvl+1)
            #print(f"Loop: current_lvl: {current_lvl}, current_xp: {current_xp}, xp_required: {xp_required}")
            #await asyncio.sleep(0.001)

            if current_xp >= xp_required:
                current_xp -= xp_required
                current_lvl +=  1
                #print(f"Loop: xp: {current_xp}, level: {current_lvl}")
            else:
                current_xp: int = current_xp
                current_lvl: int = current_lvl
                #print(f"Loop: xp: {current_xp}, level: {current_lvl}, STOPPING THE LOOP")
                return current_lvl, current_xp

    # guild : { member or message : number or [number] or {text : number}}}
    async def caller(self, option: typing.Literal["message", "voice", "reaction", "giveaway", "GLOBAL"], db: dict[int, dict[int, int | list[int] | dict[str, int]]]) -> None:
        
        async def update(Sdb: dict, option: str, guild: int, member: int) -> tuple[int | list, ...]:
            if option != "GLOBAL":
                xp: int | float = self.reaction_xp_amount if option == "reaction" else db[guild][member]["xp"] if option == "message" else db[guild][member] * self.voice_xp_amount if option == "voice" else 0
                updated_global_xp: int = Sdb["LevelingSystem"]["members"][str(member)][option]["global_xp"] + xp
                
                counter: int = Sdb["LevelingSystem"]["members"][str(member)][option]["counter" if option != "voice" else "time"] + (1 if option == "reaction" else db[guild][member] if option == "voice" else db[guild][member]["counter"] if option == "message" else 0)
                old_lvl: int = Sdb["LevelingSystem"]["members"][str(member)]["levels"][option]

                #print(f"Set data: xp: {xp}, updated_global_xp: {updated_global_xp}, counter: {counter}, old_lvl: {old_lvl}")
                current_lvl, current_xp = await self.calculate(current_xp=Sdb["LevelingSystem"]["members"][str(member)]["levels"][option], current_lvl=Sdb["LevelingSystem"]["members"][str(member)][option]["xp"] + xp)
                
                #updating global db
                Sdb["LevelingSystem"]["members"][str(member)]["GLOBAL"]["global_xp"] + xp
                Sdb["LevelingSystem"]["members"][str(member)]["GLOBAL"]["xp"] + xp
                Sdb["LevelingSystem"]["members"][str(member)]["GLOBAL"]["contribution"][option] + xp
            
            else:
                current_lvl: int = Sdb["LevelingSystem"]["members"][str(member)][option]["level"]
                current_xp: int = Sdb["LevelingSystem"]["members"][str(member)][option]["xp"]
                
                current_lvl, current_xp = await self.calculate(current_xp=current_lvl, current_lvl=current_lvl)
                old_lvl: int = Sdb["LevelingSystem"]["members"][str(member)]["GLOBAL"]["level"]

            
            roles: list[discord.Role] = []
            if current_lvl != old_lvl:
                #print("Not equal levels!")
                self.output.append({"member" : member, "option" : option, "level" : current_lvl, "guild" : guild})
                for lvl, role in Sdb["LevelingSystem"]["config"]["rewards"][option].items():
                    if current_lvl >= int(lvl) and role not in Sdb["LevelingSystem"]["members"][str(member)][option]["rewards"]:
                        roles.append(discord.Object(id=role))
                #print(f"Roles: {roles}")
                
                if roles:
                    guild_obj: discord.Guild = self.bot.get_guild(guild)
                    member_obj: discord.Member = guild_obj.get_member(member)
                    await member_obj.add_roles(*roles)
                #self.output.append({"member" : member, "option" : option, "role" : roles, "guild" : guild})
            #print("Returning...")
            if option != "GLOBAl":
                return current_lvl, counter, updated_global_xp, current_xp, roles
            else:
                return current_lvl, current_xp, roles

        def save(Sdb: dict, member: int, level: int, global_xp: int, counter: int, xp: int, roles: list[discord.Object]) -> bool:
            try:
                Sdb["LevelingSystem"]["members"][str(member)][option]["counter" if option != "voice" else "time"] = counter
                Sdb["LevelingSystem"]["members"][str(member)][option]["xp"] = xp
                Sdb["LevelingSystem"]["members"][str(member)][option]["global_xp"] = global_xp
                Sdb["LevelingSystem"]["members"][str(member)]["levels"][option] = level
                for role in roles:
                    Sdb["LevelingSystem"]["members"][str(member)][option]["rewards"].append(role.id)
                return
            except Exception as error:
                print(f"Failed to save data (lvl sys); {type(error).__name__}: {error}")
                return
        
        async def handle_global(Sdb: dict, member: int) -> None:
            lvl, xp, roles = await update(Sdb=ServerData, option="GLOBAL", guild=guild_id, member=member)
               
            Sdb["LevelingSystem"]["members"][str(member)]["GLOBAL"]["xp"] = xp
            Sdb["LevelingSystem"]["members"][str(member)]["GLOBAL"]["level"] = lvl
            for role in roles:
                ServerData["LevelingSystem"]["members"][str(member)]["GLOBAL"]["rewards"].append(role.id)
            
            self.CONNECTOR.database.save_data(server_id=guild_id, update_data=ServerData)  

        for guild_id in db: 
            ServerData: dict[str] = self.CONNECTOR.database.load_data(server_id=guild_id, serverData=True)
            if option == "reaction":
                #print(f"[caller] Executing reaction checks..")
                for message in db[guild_id]:
                    for member in db[guild_id][message]:
                        if not ServerData["LevelingSystem"]["members"].get(str(member)):
                            ServerData["LevelingSystem"]["members"][str(member)] = self.db_instance.copy()

                        lvl, counter, global_xp, xp, roles = await update(Sdb=ServerData, option=option, guild=guild_id, member=member)
                        save(Sdb=ServerData, member=member, level=lvl, global_xp=global_xp, counter=counter, xp=xp, roles=roles)
                    
                        await handle_global(Sdb=ServerData, member=member)
            else:
                for member in db[guild_id]:
                    if not ServerData["LevelingSystem"]["members"].get(str(member)):
                        ServerData["LevelingSystem"]["members"][str(member)] = self.db_instance.copy()

                    if option == "message":
                        lvl, counter, global_xp, xp, roles = await update(Sdb=ServerData, option=option, guild=guild_id, member=member)
                        save(Sdb=ServerData, member=member, level=lvl, global_xp=global_xp, counter=counter, xp=xp, roles=roles)

                    elif option == "voice":
                        lvl, time, global_xp, xp, roles = await update(Sdb=ServerData, option=option, guild=guild_id, member=member)
                        save(Sdb=ServerData, member=member, level=lvl, global_xp=global_xp, counter=time, xp=xp, roles=roles)
                    
                    await handle_global(Sdb=ServerData, member=member)

    async def sender(self) -> None:
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            while self.output:
                msg_data: dict[str, int | str] = self.output[0]
                #print(f"[sender] Executing first argument: {msg_data}")
                ServerData: dict[str] = self.CONNECTOR.database.load_data(server_id=msg_data["guild"], serverData=True)

                if ServerData["LevelingSystem"]["config"]["notifications"]["dm"]["send"]:
                    member: discord.Member = self.bot.get_guild(msg_data["guild"]).get_member(msg_data["member"])
                    try:
                        #print(f"[sender] Creating dm with {member}.")
                        dm: discord.DMChannel = await member.create_dm()
                        #print(f"[sender] Sending message to {member}.")
                        #if msg_data.get("role"):
                            #await dm.send(f"Congrats {member.mention if ServerData["LevelingSystem"]["config"]["notifications"]["dm"]["ping"] else member.display_name}, you just recieved {', '.join()}")
                        #else:                       
                        await dm.send(ServerData["LevelingSystem"]["config"]["notifications"]["dm"]["message"].format(member=member.mention if ServerData["LevelingSystem"]["config"]["notifications"]["dm"]["ping"] else member.display_name, type=msg_data["option"], num=msg_data["level"]))
                    except Exception as error:
                        #print(f"[sender] Failed to send dm message to member {member}. {error}")
                        pass

                if ServerData["LevelingSystem"]["config"]["notifications"]["guild"]["send"] and ServerData["Logging"]["LevelingSystem"]:
                    member: discord.Member = self.bot.get_guild(msg_data["guild"]).get_member(msg_data["member"])
                    channel: discord.TextChannel = self.bot.get_guild(msg_data["guild"]).get_channel(ServerData["Logging"]["LevelingSystem"])
                    try:
                        #print(f"[sender] Sending message to {channel}.")
                        await channel.send(ServerData["LevelingSystem"]["config"]["notifications"]["guild"]["message"].format(member=member.mention if ServerData["LevelingSystem"]["config"]["notifications"]["guild"]["ping"] else member.display_name, type=msg_data["option"], num=msg_data["level"]))
                    except Exception as error:
                        #print(f"[sender] Failed to send message to {channel}. {error}")
                        pass

                self.output.pop(0)
                await asyncio.sleep(1)
            await asyncio.sleep(1)
