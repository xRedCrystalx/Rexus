import discord, sys, datetime, asyncio, random
sys.dont_write_bytecode = True
from discord.ext import commands
import connector as syscon
from core.old_root.LevelingSystem import LevelingSystem


class LevelingListener:
    def __init__(self) -> None:
        self.CONNECTOR: syscon.SysConnector = syscon.sys_connector
        self.bot: commands.Bot = self.CONNECTOR.bot
        self.path: str = self.CONNECTOR.path
        self.interval_in_minutes: int = 1
        self.max_msg_xp, self.msg_xp_amount= (16, 2)
        self.levelingsystem: LevelingSystem = self.CONNECTOR.lvlSys
        
        self.msg_db: dict[int, dict[int, dict[str, int]]] = {}
        self.voice_db: dict[int, dict[int, int]] = {}
        self.reaction_db: dict[int, dict[int, list[int]]] = {}

    async def clock(self) -> None:
        await self.bot.wait_until_ready()
        #print("[clock] Starting the loop..")
        while not self.bot.is_closed():
            #print("[clock] Sending DB to caller (message)..")
            await self.levelingsystem.caller(option="message", db=self.msg_db)
            self.msg_db.clear()
            #print("[clock] Sending DB to caller (reaction)..")
            await self.levelingsystem.caller(option="reaction", db=self.reaction_db)
            self.reaction_db.clear()    
            await asyncio.sleep(self.interval_in_minutes * 60)

    async def message_handler(self, message: discord.Message) -> None:
        if not (message.guild is None or message.author.bot or type(message.author) == discord.User):
            #print("[message_handler] Recieved message argument.")
            ServerData: dict =  self.CONNECTOR.database.load_data(server_id=message.guild.id, serverData=True)
            if ServerData["Plugins"]["LevelingSystem"] and ServerData["LevelingSystem"]["config"]["levels"]["message"]:
                #print("[message_handler] Saving to RAM database.")
                if self.msg_db.get(message.guild.id):
                    if self.msg_db[message.guild.id].get(message.author.id):
                        self.msg_db[message.guild.id][message.author.id]["xp"] += self.msg_xp_amount if self.msg_db[message.guild.id][message.author.id]["xp"] + self.msg_xp_amount < self.max_msg_xp else 0
                        self.msg_db[message.guild.id][message.author.id]["counter"] += 1
                    else:
                        self.msg_db[message.guild.id][message.author.id] = {"counter" : 1, "xp" : self.msg_xp_amount}
                else:
                    self.msg_db[message.guild.id] = {}
                    self.msg_db[message.guild.id][message.author.id] = {"counter" : 1, "xp" : self.msg_xp_amount}
                #print("[message_handler] Saved.")

    async def voice_handler(self, member: discord.Member | discord.User, update: discord.VoiceState) -> None:
        ServerData: dict = self.CONNECTOR.database.load_data(server_id=member.guild.id, serverData=True)
        #print("[voice_handler] Recieved voice argument.")
        #print(f"Channel: {update.channel}; Mute: {update.self_mute}; Deaf: {update.self_deaf}")
        
        if ServerData["Plugins"]["LevelingSystem"] and ServerData["LevelingSystem"]["config"]["levels"]["voice"]:
            if not (member.bot or type(member) == discord.User):
                if update.channel:
                    if self.voice_db.get(member.guild.id) is None:
                        #print("[voice_handler] Created db for ", member.guild.id)
                        self.voice_db[member.guild.id] = {}
                    
                    if update.self_deaf is False and update.self_mute is False:
                        #print("[voice_handler] starting timer for ", member.id)
                        self.voice_db[member.guild.id][member.id] = datetime.datetime.timestamp(datetime.datetime.now()) if self.voice_db[member.guild.id].get(member.id) is None else self.voice_db[member.guild.id][member.id]
                    else:
                        if self.voice_db[member.guild.id].get(member.id):
                            #print("[voice_handler] stoping timer [status change] for ", member.id)
                            await self.levelingsystem.caller(option="voice", db={member.guild.id : {member.id : int(datetime.datetime.timestamp(datetime.datetime.now()) - self.voice_db[member.guild.id][member.id])}})
                            self.voice_db[member.guild.id].pop(member.id)
                else:
                    if self.voice_db[member.guild.id].get(member.id):
                        #print("[voice_handler] Sending DB to caller (voice)..")
                        #print("[voice_handler] stoping timer [left vc] for ", member.id)
                        await self.levelingsystem.caller(option="voice", db={member.guild.id : {member.id : int(datetime.datetime.timestamp(datetime.datetime.now()) - self.voice_db[member.guild.id][member.id])}})
                        self.voice_db[member.guild.id].pop(member.id)

    async def reaction_handler(self, reaction: discord.RawReactionActionEvent) -> None:
        if reaction.guild_id:
            ServerData: dict = self.CONNECTOR.database.load_data(server_id=self.bot.get_guild(reaction.guild_id).id, serverData=True)
            #print("[reaction_handler] Recieved rection argument.")
            if ServerData["Plugins"]["LevelingSystem"] and ServerData["LevelingSystem"]["config"]["levels"]["reaction"]:
                if not (reaction.member.bot or type(reaction.member) == discord.User or reaction.member is None):
                    #print("[reaction_handler] Saving to RAM database.")
                    if guild_db := self.reaction_db.get(reaction.guild_id):
                        if guild_db.get(reaction.message_id):
                            if reaction.member.id not in self.reaction_db[reaction.guild_id][reaction.message_id]:
                                self.reaction_db[reaction.guild_id][reaction.message_id].append(reaction.member.id)
                        else:
                            self.reaction_db[reaction.guild_id][reaction.message_id] = [reaction.member.id]
                    else:
                        self.reaction_db[reaction.guild_id] = {}
                        self.reaction_db[reaction.guild_id][reaction.message_id] = [reaction.member.id]
                    #print("[reaction_handler] Saved.")
