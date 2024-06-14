import sys, typing, os
sys.dont_write_bytecode = True
import src.connector as con
from src.core.helpers.errors import report_error

from xRedUtils import files
from xRedUtils.type_hints import SIMPLE_ANY

class Database:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared
        self.config_path: str = f"{self.shared.path}/src/config.json"
        self.databases_path: str = self.shared.path+"/databases/{type}/{id}.json"
        self.template_path: str = self.shared.path+"/databases/{type}.json"
    
    def load_data(self, id: int | None = None, db: str = "guilds") -> dict[str, SIMPLE_ANY]:
        if id:
            try:
                database = files.open_file(self.databases_path.format(type=db, id=id), decoder="json")
            except FileNotFoundError:
                database: dict[str, SIMPLE_ANY] = self.create_database(id, db)
            
            return database
        else:
            return files.open_file(self.config_path, decoder="json")

    def save_data(self, id: int, update_data: dict, db: str = "guilds") -> None:
        if id:
            files.save_file(self.databases_path.format(type=db, id=id), update_data, encoder="json", indent=4)
        else:
            files.save_file(self.config_path, update_data, encoder="json", indent=4)
    
    def create_database(self, id: str | int, option: str = "guilds") -> dict[str, typing.Any]:
        try:
            template: dict = files.open_file(self.template_path.format(type="user_template" if option == "member" else "guild_template"), decoder="json")
            files.save_file(self.databases_path.format(type=option, id=id), template, encoder="json")
        except Exception as error:
            report_error(error, self.create_database, "full")


    # FIX THESE ˇˇˇˇˇˇ
    def add_value(self, key: str, value_type: typing.Literal["str", "int", "bool", "list", "dict", "none"], path: str | None = None, db_id: int | None = None) -> bool:
        values: dict[str, typing.Any] = {
            "str" : "",
            "int" : 0,
            "bool" : False,
            "list" : [],
            "dict" : {},
            "none" : None
        }

        def recursive_add_value(d, path_segments):
            if not path_segments:
                # We've reached the target level, so add the key-value pair
                d[key] = values.get(value_type)
            else:
                # Continue navigating the path
                current_segment = path_segments[0]
                if current_segment == '*':
                    for k, v in d.items():
                        if isinstance(v, dict):
                            recursive_add_value(v, path_segments[1:])
                        elif isinstance(v, list):
                            for item in v:
                                recursive_add_value(item, path_segments[1:])
                elif current_segment in d:
                    recursive_add_value(d[current_segment], path_segments[1:])

        if not db_id:
            for file in os.listdir(f"{self.shared.path}/database"):
                if file.endswith(".json"):
                    serverID = int(file.removesuffix(".json"))
                    main: dict = self.load_data(server_id=serverID, serverData=True)
                    db = main
                    try:
                        if path:
                            recursive_add_value(db, path.split("."))
                        else:
                            # Handle the case when no path is provided
                            for k, v in db.items():
                                if isinstance(v, dict):
                                    recursive_add_value(v, path.split("."))
                                elif isinstance(v, list):
                                    for item in v:
                                        recursive_add_value(item, path.split("."))

                        self.save_data(server_id=serverID, update_data=main)
                    
                    except Exception as error:
                        print(f"Could not create a new key/value pair in the DB. {type(error).__name__}: {error}")
                        return False
        else:
            main: dict = self.load_data(server_id=db_id, serverData=True)
            db: dict = main
            try:
                if path:
                    recursive_add_value(db, path.split("."))
                else:
                    # Handle the case when no path is provided
                    for k, v in db.items():
                        if isinstance(v, dict):
                            recursive_add_value(v, path.split("."))
                        elif isinstance(v, list):
                            for item in v:
                                recursive_add_value(item, path.split("."))

                self.save_data(server_id=db_id, update_data=main)
            except Exception as error:
                print(f"Could not create a new key/value pair in the DB. {type(error).__name__}: {error}")
                return False

    def remove_value(self, key: str, path: str = None, db_id: int = None) -> bool:
        if not db_id:
            for file in os.listdir(f"{self.shared.path}/database"):
                if file.endswith(".json"):
                    serverID = int(file.removesuffix(".json"))
                    main: dict = self.load_data(server_id=serverID, serverData=True)
                    db = main
                    try:
                        for p in path.split("."):
                            db = db[p]
                        db.pop(key)
                        self.save_data(server_id=serverID, update_data=main)
                    except Exception as error:
                        print(f"Could not remove key from the DB. {type(error).__name__}: {error}")
                        return
        else:
            main: dict = self.load_data(server_id=db_id, serverData=True)
            db: dict = main            
            try:
                for p in path.split("."):
                    db = db[p]
                db.pop(key)    
                self.save_data(server_id=db_id, update_data=main)
            except Exception as error:
                print(f"Could not remove key from the DB. {type(error).__name__}: {error}")  
                return