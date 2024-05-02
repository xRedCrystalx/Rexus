import sys, discord, asyncio, typing, datetime
sys.dont_write_bytecode = True
import src.connector as con 

if typing.TYPE_CHECKING:
    from discord.ext import commands

class LevelingSystem:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = self.shared.bot
        self.loop: asyncio.AbstractEventLoop = self.shared.loop

        # guilds > users > types
        self.database: dict[int, dict[int, dict[str, int]]] = {}
        self.base_user_db: dict[str, typing.Any] = {
            "message": 0,
            "reaction": {
                "counter": 0,
                "messages": []
            },
            "voice": {
                "start": None,
                "channel": None,
                "time": 0
            }
        }
        self._math()

    def _math(self) -> None:
        delta, delta_a, delta_b = (0, 0, 0)

        levels: list[int] = [1,2,3]
        xp_values: list[int] = [100, 155, 220]

        for i in range(3):
            k: int = (i + 1) % 3
            delta += ((i+1) ** 2) * (k+1 - levels[(i + 2) % 3])
            delta_a += xp_values[i] * (k+1 - levels[(i + 2) % 3])
            delta_b += ((i+1) ** 2) * (xp_values[k] - xp_values[(i + 2) % 3])

        self.level_value_a: float = delta_a / delta
        self.level_value_b: float = delta_b / delta
        self.level_value_c: float = xp_values[0] - self.level_value_a * (levels[0] ** 2) - self.level_value_b * levels[0]

    def _get_local_db(self, db: dict, key: str, creation: dict) -> dict:
        if data := db.get(key):
            return data
        else:
            if creation:
                db[key] = {}.update(creation)
            else:
                db[key] = {}
            return db.get(key)

    async def listener(self, guild_db: dict[str, typing.Any], **kwargs) -> None:
        #db = self.database
        if guild_db["leveling_system"]["status"]:
            if (message := kwargs.get("message")) and isinstance(message, discord.Message) and guild_db["leveling_system"]["levels"]["message"]:
                if not message.guild or message.author.bot or isinstance(message.author, discord.User):
                    return

                local_guild_users_db: dict = self._get_local_db(self.database, message.guild.id)
                local_user_db: dict = self._get_local_db(local_guild_users_db, message.author.id, creation=self.base_user_db)    

                if local_user_db["message"] >= 40:
                    return
                local_user_db["message"] += 1
            
            elif (reaction := kwargs.get("reaction")) and isinstance(reaction, discord.RawReactionActionEvent) and guild_db["leveling_system"]["levels"]["reaction"]:
                if not reaction.member or reaction.member.bot or not reaction.guild_id:
                    return
                
                local_guild_users_db: dict = self._get_local_db(self.database, reaction.guild_id)
                local_user_db: dict = self._get_local_db(local_guild_users_db, reaction.member.id, creation=self.base_user_db)

                if reaction.message_id in local_user_db["reaction"]["messages"]:
                    return
                
                local_user_db["reaction"]["messages"].append(reaction.message_id)
                local_user_db["reaction"]["counter"] += 1

            elif (member := kwargs.get("member")) and (update := kwargs.get("after")) and isinstance(update, discord.VoiceState) and isinstance(member, discord.Member) and guild_db["leveling_system"]["levels"]["voice"]:
                if member.bot and guild_db["leveling_system"]["levels"]["voice"]:
                    return
                
                local_guild_users_db: dict = self._get_local_db(self.database, member.guild.id)
                local_user_db: dict = self._get_local_db(local_guild_users_db, member.id, creation=self.base_user_db)
                current_time: int = int(datetime.datetime.timestamp(datetime.datetime.now()))

                if update.channel:
                    if local_user_db["voice"]["channel"] == update.channel.id:
                        if update.self_mute and update.self_deaf:
                            local_user_db["voice"]["time"] += current_time - local_user_db["voice"]["start"]
                            local_user_db["voice"]["start"] = None
                        
                        else:
                            local_user_db["voice"]["start"] = current_time
                    else:
                        local_user_db["voice"]["start"] = current_time
                        local_user_db["voice"]["channel"] = update.channel.id
                else:
                    local_user_db["voice"]["time"] += current_time - local_user_db["voice"]["start"]
                    local_user_db["voice"]["channel"] = None
                    local_user_db["voice"]["start"] = None
        return
    
    def check_user_level_up(self, user_id: int, guild_id: int) -> None:
        main_user_db: dict[str, typing.Any] = self.shared.db.load_data(user_id, "USER")
        user_db: dict[str, dict[str, int]] = main_user_db

        for level in user_db["levels"]:
            # level up
            while True:
                current_lvl: int = user_db[str(guild_id)]["levels"][level]["level"]
                current_xp: int = user_db[str(guild_id)]["levels"][level]["current_xp"]
                next_lvl_xp: int = self.calculate_xp(current_lvl+1)

                if current_xp >= next_lvl_xp:
                    user_db[str(guild_id)]["levels"][level]["current_xp"] -= next_lvl_xp
                    user_db[str(guild_id)]["levels"][level]["level"] +=  1
                else:
                    break
        
            # rewards
            current_lvl: int = user_db[str(guild_id)]["levels"][level]["level"]
            guild_db: dict[str, typing.Any] = self.shared.db.load_data(guild_id)
            
            roles: list[discord.Object] = []
            for required_lvl, reward in guild_db["leveling_system"]["rewards"][level].items():
                if current_lvl >= int(required_lvl) and reward not in user_db[guild_id]["levels"]["GLOBAL"]["rewards"]:
                    roles.append(discord.Object(reward))

            if roles:
                guild_obj: discord.Guild = self.bot.get_guild(guild_id)
                member_obj: discord.Member = guild_obj.get_member(user_id)
                self.shared.sender.resolver([])
                #member_obj.add_roles(*roles)

            
                
        
        
        
        self.shared.db.save_data(user_id, user_db, db="USER")

    def guild_updater(self, guild_id: int) -> None:
        for user_id in self.database.get(guild_id):
            main_user_db: dict[str, typing.Any] = self.shared.db.load_data(user_id, "USER")
            user_db = main_user_db
            local_user_db: dict[str, dict[str, int | list[int]]] = self.database[guild_id][user_id]

            # db creation
            if not user_db.get(str(guild_id)):
                user_db[str(guild_id)] = {}
                self.shared.db.save_data(user_id, user_db, db="USER")

            if not user_db[str(guild_id)].get("leveling"):
                user_db[str(guild_id)]["leveling"] = {
                    "GLOBAL": {
                        "level": 0,
                        "counter": 0,
                        "current_xp": 0,
                        "global_xp": 0,
                        "rewards": [],
                        "achievements": []
                    },
                    "message": {
                        "level": 0,
                        "counter": 0,
                        "current_xp": 0,
                        "global_xp": 0
                    },
                    "voice": {
                        "level": 0,
                        "counter": 0,
                        "current_xp": 0,
                        "global_xp": 0
                    },
                    "reaction": {
                        "level": 0,
                        "counter": 0,
                        "current_xp": 0,
                        "global_xp": 0
                    }
                }
                self.shared.db.save_data(user_id, user_db, db="USER")

            # XP calculation
            for level_type in local_user_db:
                ...

            self.check_user_level_up(user_id, guild_id)


    def calculate_xp(self, level: int) -> int:
        return int(self.level_value_a * level ** 2 + self.level_value_b * level + self.level_value_c)

    async def start(self) -> None:
        while True:
            asyncio.sleep(60 * 5)

            for guild_id in self.database:
                self.guild_updater(guild_id)

            self.database.clear()


"""
leaderboard:

user_dbs: list[str] = os.listdir("./databases/users")

for member in guild.members:
    if f"{member.id}.json" in user_dbs:
        self.shared.db.load_data(member.id, "USER")


WORK IN PROGRESS

"""
