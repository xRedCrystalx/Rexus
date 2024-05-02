import sys, json, typing, os
sys.dont_write_bytecode = True
import src.connector as con

class Database:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared
        self.config_path: str = f"{self.shared.path}/src/config.json"
        self.databases_path: str = self.shared.path+"/databases/{type}/{id}.json"
        self.template_path: str = self.shared.path+"/databases/{type}.json"

    def _open_file(self, path: str, mode: str = "r") -> dict:
        try:
            with open(path, mode, encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            self.shared.logger.log(f"@databaseHandler._open_file: Error trying to load data for `{path}`.\n{self.shared.errors.full_traceback()}", "ERROR")

    def _name_resolver(self, name: str) -> str:
        return "users" if str(name).upper() in ["USERS", "USER", "MEMBER", "MEMBERS"] else "guilds"
    
    def load_data(self, id: int | None = None, db: str = "guilds") -> dict[str, typing.Any]:
        if id:
            if not (database := self._open_file(self.databases_path.format(type=self._name_resolver(db), id=id))):
                database: dict[str, typing.Any] = self.create_database(id, db)
            return database
        else:
            return self._open_file(self.config_path)

    def save_data(self, id: int, update_data: dict, db: str = "guilds") -> None:
        try:
            with open(self.databases_path.format(type=self._name_resolver(db), id=id), "w", encoding="utf-8") as old_data:
                json.dump(update_data, old_data, indent=4)
        except Exception as error:
            self.shared.logger.log(f"@databaseHandler.save_data: Error trying to save data for {id}.\n{self.shared.errors.full_traceback()}", "ERROR")

    def create_database(self, id: str | int, option: str = "guilds") -> dict[str, typing.Any]:
        try:
            template: dict = self._open_file(self.template_path.format(type="user_template" if option == "user" else "guild_template"))
            
            with open(self.databases_path.format(type=self._name_resolver(option), id=id), "w", encoding="utf-8") as new_file:
                json.dump(template, new_file, indent=4)
        
        except Exception:
            self.shared.logger.log(f"@databaseHandler.create_database: Error trying to save data for {id}.\n{self.shared.errors.full_traceback()}", "ERROR")

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