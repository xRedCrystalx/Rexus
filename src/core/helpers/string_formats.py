import sys, discord, typing, ast, re
sys.dont_write_bytecode = True
import src.connector as con
from xRedUtils.times import seconds_to_str

class StringFormats:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared

    def boolean_format(self, boolean: bool, option: typing.Literal["switch", "y/n"] = "switch")-> str:
        self.shared.logger.log(f"@StringFormats.boolean_format > kwargs: boolean: {boolean}, option: {option}", "NP_DEBUG")
        if option == "y/n":
            return "Yes" if boolean else "No"
        elif option == "switch":
            return "Enabled" if boolean else "Disabled"

    def id_format(self, id: int, option: typing.Literal["channel", "role", "member"]) -> str:
        self.shared.logger.log(f"@StringFormats.id_format > kwargs: id: {id}, option: {option} ", "NP_DEBUG")
        try:
            id = int(id)
        except: pass

        return f"`{id}`" if not isinstance(id, int) else f"<#{id}>" if option == "channel" else f"<@&{id}>" if option == "role" else f"<@!{id}>" if option == "user" else "Error"

    def resolve_id(self, id: int | str, guild: discord.Guild | int, var: str = None) -> discord.abc.GuildChannel | discord.User | discord.Member | discord.Role:
        def obj(ID: int, guild: discord.Guild) -> object:
            try:
                if channel := guild.get_channel(ID):
                    return channel
                elif role := guild.get_role(ID):
                    return role
                elif member := guild.get_member(ID):
                    return member
            except Exception:
                self.shared.logger.log( f"@ConfigPages.resolve_id.obj > {self.shared.errors.full_traceback()}", "ERROR")

        try:
            self.shared.logger.log(f"@StringFormats.resolve_id > kwargs: id: {id}, guild: {guild}, var: {var}", "NP_DEBUG")
            if isinstance(guild, discord.Guild) or (guild := self.shared.bot.get_guild(int(guild))):
                discord_object = obj(int(id), guild)
                self.shared.logger.log(f"@StringFormats.resolve_id > Returned object: {discord_object}", "NP_DEBUG")

                if not var:
                    return discord_object
                else:
                    return getattr(discord_object, var)

        except (ValueError, TypeError):
            return f"`{id}`"
        
        except Exception:
            self.shared.logger.log( f"@ConfigPages.resolve_id > {self.shared.errors.full_traceback()}", "ERROR")

    def list_format(self, value: list, sep: typing.Literal["comma", "point"] = "point") -> str | None:
        self.shared.logger.log(f"@StringFormats.list_format > kwargs: value: {value}, sep: {sep} ", "NP_DEBUG")
        if isinstance(value, (tuple, list)):
            if sep == "comma":
                return ", ".join(map(str, value))
            elif sep == "point":
                return "\n".join([f"- {item}" for item in value])

    def discord_format(self, var: str, format: str = "CODE") -> str:
        self.shared.logger.log(f"@StringFormats.discord_format > kwargs: var: {var}, format: {format}", "NP_DEBUG")
        if format == "CODE":
            return f"`{var}`"
        elif format == "BOLD":
            return f"**{var}**"
        elif format == "ITALIC":
            return f"*{var}*"
        elif format == "UNDERLINE":
            return f"__{var}__"
        else:
            return var

    def completion_bar(self, total: int, completed: int, _len: int = 15) -> str:
        self.shared.logger.log(f"@StringFormats.completion_bar > kwargs: total: {total}, completed: {completed}, _len: {_len}", "NP_DEBUG")
        percentage: float = (completed / total) * 100
        completed_bar = int(_len * percentage / 100)
        remaining_bar: int = _len - completed_bar
        bar: str = "[" + "#" * completed_bar + "-" * remaining_bar + "]"
 
        return f"{bar} {percentage:.1f}%"
    
    def placeholder(self, string: str) -> str:
        return string

    def time_converter(self, seconds: int) -> str:
        return seconds_to_str(seconds)

    def format(self, string: str, db: dict) -> str:
        def handle_functions(value: str, funcs: str) -> typing.Any:
            self.shared.logger.log(f"@StringFormats.format.handle_functions > kwargs: value: {value}, funcs: {value}", "NP_DEBUG")
            try:
                functions: list[tuple[str, dict[str, typing.Any]]] = []

                for func in funcs.split("&"):
                    if len(data := func.split("?")) <= 1:
                        functions.append([data[0].strip(), {}])
                    else:
                        kwargs: dict[str, typing.Any] = {k: ast.literal_eval(v) for k, v in (param.split("=") for param in map(str.strip, data[1].split(",")))}
                        functions.append([data[0].strip(), kwargs])

                self.shared.logger.log(f"@StringFormats.format.handle_functions > Found {len(functions)} functions. {functions}", "NP_DEBUG")

                for function, arguments in functions:                
                    if function and (callable_function := getattr(self, function)):
                        if isinstance(value, (list, tuple)) and function not in ["list_format"]: # exception list for funcs that require iterable
                            value = [callable_function(x, **arguments) for x in value]
                        else:
                            value = callable_function(value, **arguments)
                return value

            except Exception:
                self.shared.logger.log(f"@StringFormats.format.handle_functions > {self.shared.errors.full_traceback()}", "ERROR")
            return 
        
        try:
            placeholders: list[tuple[str, str]] = re.findall(r"\{([^:}]+)(?::([^}]+))?\}", string)
            self.shared.logger.log(f"@StringFormats.format > Found {len(placeholders)} placeholders. {placeholders}", "NP_DEBUG")

            for value_path, funcs in placeholders:
                value_path, funcs = (value_path.strip(), funcs.strip())

                # handling non-func placeholders
                if not funcs:
                    placeholder: str = "{"+value_path+"}"
                    self.shared.logger.log(f"@StringFormats.format > Replacing non-func placeholder {placeholder}.", "NP_DEBUG")
                    string = string.replace(placeholder, placeholder.format(**db))
                
                # function placeholder
                placeholder: str = "{"+f"{value_path}:{funcs}"+"}"
                self.shared.logger.log(f"@StringFormats.format > Handling {placeholder} placeholder.", "NP_DEBUG")

                # getting path value
                try:
                    value: typing.Any =  ast.literal_eval(("{"+value_path+"}").format(**db))
                except:
                    try:
                        value: str = ("{"+value_path+"}").format(**db)
                    except Exception:
                        value = "`None`"

                self.shared.logger.log(f"@StringFormats.format > Got {placeholder}'s value {value}.", "NP_DEBUG")
                
                # if the value is dict > formatting both key and value
                if isinstance(value, dict):
                    self.shared.logger.log(f"@StringFormats.format > Detected dictionary as value.", "NP_DEBUG")
                    # both key and values must exist
                    keys = tuple(value.keys())
                    values = tuple(value.values())

                    if not keys or not values:
                        self.shared.logger.log(f"@StringFormats.format > Missing keys or values, ignoring.", "TESTING")
                        string = string.replace(placeholder, "")
                        continue

                    # getting functions
                    functions: list[str] = funcs.split("|")
                    if len(functions) == 2:
                        final_functions: str | None = functions[-1].split(">")[-1] if ">" in functions[-1] else None

                        # fornatting keys and values
                        formatted_keys: str | list[str]= handle_functions(keys, functions[0])
                        formatted_values: str | list[str] = handle_functions(values, functions[-1].split(">")[0])

                        self.shared.logger.log(f"@StringFormats.format > Formatted keys and values.", "NP_DEBUG")

                        formatted: list[str] = [f"{key}: {formatted_values[index]}" for index, key in enumerate(formatted_keys)]
                        self.shared.logger.log(f"@StringFormats.format > Connected keys and values.", "NP_DEBUG")
                        
                        # final formatting/replacing placeholder
                        if final_functions:
                            formatted = handle_functions(formatted, final_functions)
                            self.shared.logger.log(f"@StringFormats.format > Final formatting.", "NP_DEBUG")

                        self.shared.logger.log(f"@StringFormats.format > Replacing {placeholder} with {formatted}.", "NP_DEBUG")
                        string = string.replace(placeholder, str(formatted))
                else:
                    value = str(handle_functions(value, funcs))
                    self.shared.logger.log(f"@StringFormats.format > Replacing {placeholder} with {value}", "NP_DEBUG")
                    string = string.replace(placeholder, value)
            
            return string

        except Exception:
            self.shared.logger.log( f"@StringFormats.format >\n{self.shared.errors.full_traceback()}", "ERROR")
        return
