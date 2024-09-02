import sys, aiomysql, asyncio, typing
sys.dont_write_bytecode = True
from src.connector import shared
from src.core.helpers.errors import report_error

from xRedUtilsAsync.dicts import json_to_dict, dict_to_json
from xRedUtilsAsync.type_hints import SIMPLE_ANY

class DatabaseManager:
    def __init__(self, name: str, minsize: int = 5, maxsize: int = 25, pool_recycle: int = 3600, **kwargs) -> None:
        self.name: str = name

        self.loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        self.pool: aiomysql.Pool = aiomysql.Pool(minsize=minsize, maxsize=maxsize, pool_recycle=pool_recycle, cursorclass=aiomysql.DictCursor, echo=False, loop=asyncio.get_running_loop(), **kwargs)

    def isJson(self, s: str) -> bool:
        return s.endswith("}") and s.startswith("{")

    def handle_single(d: dict[str, SIMPLE_ANY]) -> dict[SIMPLE_ANY] | SIMPLE_ANY:
        if len( values := d.values() ) > 1:
            return values[0]
        return d

    async def json_codec(self, d: dict[str, SIMPLE_ANY] | str, option: typing.Literal["encode", "decode"] = "decode") -> dict[str, SIMPLE_ANY] | SIMPLE_ANY:
        if not self.isJson(d):
            return d
        
        try:
            if option == "decode":
                return json_to_dict(d)
            else:
                return dict_to_json(d)

        except Exception as error:
            return d

    async def better_execute(self, query: str, args: list[SIMPLE_ANY] = None) -> list[dict[str, SIMPLE_ANY]] | None:
        async with self.pool.acquire() as con:
            con: aiomysql.Connection
            await con.begin()

            async with con.cursor() as cursor:
                cursor: aiomysql.DictCursor

                try:
                    await cursor.execute(query, args if args else [])
                    await con.commit()

                    return await cursor.fetchall()

                except Exception:
                    await con.rollback()
                    await report_error(self.better_execute, "simple", None)

    async def select_data(self, id: int, table: str, columns: list[str] = "*", many: bool | int = False) -> dict[str, SIMPLE_ANY] | list[dict[str, SIMPLE_ANY]] | list[SIMPLE_ANY] | SIMPLE_ANY | None:
        selection: list[dict[str, SIMPLE_ANY]] | None = await self.better_execute(
            f"SELECT {columns if not isinstance(columns, list) else " ,".join(columns)} FROM {table} WHERE id = %s", [id]
        )

        if selection:
            if many:
                result: list[dict[str, SIMPLE_ANY]] = selection if isinstance(many, bool) else (selection[:many] if len(selection) >= many else selection)
                return [
                    self.handle_single({ key: await self.json_codec(value, "decode") for key, value in group.items() })
                    for group in selection
                ]

            else:
                result: dict[str, SIMPLE_ANY] = selection[0] 
                return self.handle_single({ key: await self.json_codec(value, "decode") for key, value in result.items() })

    async def update_data(self, id: int, table: str, data: dict[str, SIMPLE_ANY]) -> None:                        
        await self.better_execute(
            f"UPDATE {table} SET {", ".join([f"{column} = %s" for column in data.keys()])} WHERE id = %s", 
            [await self.json_codec(value, "encode") for value in data.values()] + [id]
        )

    async def dict_updater(self, table: str, column: str, path: str, key: str, value: str = "_REM", id: list[int] = None) -> dict[str, SIMPLE_ANY]:
        def recursive(d: dict[str, SIMPLE_ANY], path_segments) -> None:
            if path_segments:
                current_segment: str = path_segments[0]
                if current_segment == '*':
                    for value in d.values():
                        if isinstance(value, dict):
                            recursive(value, path_segments[1:])
                        
                        elif isinstance(value, list):
                            for item in value:
                                recursive(item, path_segments[1:])
                
                elif current_segment in d:
                    recursive(d[current_segment], path_segments[1:])
            else:
                if value == "_REM":
                    d.pop(key, None)
                else:
                    d[key] = value
        
        if id:
            for indentifier in id:
                local_copy: dict[str, SIMPLE_ANY] | None = await self.select_data(indentifier, table, column)

                if local_copy:
                    local_editable = local_copy
                    recursive(local_editable, path.split("."))

                    await self.update_data(indentifier, table, {column: local_copy})
        else:
            page_number = 1
            while True:
                offset: int = (page_number - 1) * 50

                rows: list[dict] = await self.better_execute(f"SELECT id, {column} FROM {table} LIMIT 50 OFFSET {offset}")
                if not rows:
                    break
                
                for row in rows:
                    identifier: int = row.get("id")
                    local_copy: dict[str, SIMPLE_ANY] = row.get(column)
                    local_editable = local_copy

                    if local_editable:
                        recursive(local_editable, path.split("."))

                    await self.update_data(identifier, table, {column: local_copy})

                page_number += 1

async def setup(bot) -> None:
    connection_data: dict[str, str] = {
        "host": "192.168.96.136",
        "port": 3306,
        "charset": "utf8mb4",
        "db": "Rexus"
    }

    await shared.module_manager.load(DatabaseManager(name="read-agent", user="DevRexus", password="root", **connection_data),
        config={
            "module": True,
            "location": shared,
            "var": "db_read"
    })
    await shared.module_manager.load(DatabaseManager(name="write-agent", user="DevRexus", password="root", **connection_data),
        config={
            "module": True,
            "location": shared,
            "var": "db_write"
    })