import sys, discord, typing, ast, re
sys.dont_write_bytecode = True
import src.connector as con

class StringFormats:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared

    def boolean_format(self, boolean: bool, option: typing.Literal["switch", "y/n"] = "switch")-> str:
        if option == "y/n":
            return "Yes" if boolean else "No"
        elif option == "switch":
            return "Enabled" if boolean else "Disabled"

    def id_format(self, id: int, option: typing.Literal["channel", "role", "member"]) -> str:
        try:
            id = int(id)
        except: pass

        return "`None`" if not id else f"`{id}`" if not isinstance(id, int) else f"<#{id}>" if option == "channel" else f"<@&{id}>" if option == "role" else f"<@!{id}>" if option == "user" else "Error"

    def resolve_id(self, id: int | str, guild: discord.Guild | int, var: str = None) -> discord.abc.GuildChannel | discord.User | discord.Member | discord.Role:
        def obj(ID: int) -> object:
            try:
                if channel := guild.get_channel(ID):
                    return channel
                elif role := guild.get_role(ID):
                    return role
                elif member := guild.get_member(ID):
                    return member
            except Exception as error:
                self.shared.logger.log( f"@ConfigPages.resolve_id.obj > {type(error).__name__}: {error}", "ERROR")

        try:
            if not guild:
                return id

            if isinstance(guild, discord.Guild) or (guild := self.shared.bot.get_guild(guild)):
                if not var:
                    return obj(int(id))
                else:
                    return getattr(obj(int(id)), var)

        except (ValueError, TypeError):
            return f"`{id}`"
        except Exception as error:
            self.shared.logger.log( f"@ConfigPages.resolve_id > {type(error).__name__}: {error}", "ERROR")

    def list_format(self, value: list, sep: typing.Literal["comma", "point"] = "point") -> str | None:
        try:
            if isinstance(value, (tuple, list)):
                if sep == "comma":
                    return ", ".join(map(str, value))
                elif sep == "point":
                    return "\n".join([f"- {item}" for item in value])

        except Exception as error:
            self.shared.logger.log( f"@StringFormats.list_format > {type(error).__name__}: {error}", "ERROR")
        return
    
    def discord_format(self, var: str, format: str = "CODE") -> str:
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
        percentage: float = (completed / total) * 100
        completed_bar = int(_len * percentage / 100)
        remaining_bar: int = _len - completed_bar
        bar: str = "[" + "#" * completed_bar + "-" * remaining_bar + "]"
 
        return f"{bar} {percentage:.1f}%"
    

    def format(self, string: str, kwargs) -> str:
        def handle_functions(value: str, funcs: str) -> typing.Any:
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

            except Exception as error:
                self.shared.logger.log(f"@StringFormats.format.handle_functions > {type(error).__name__}: {error}", "ERROR")
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
                    string = string.replace(placeholder, placeholder.format(**kwargs))
                
                # function placeholder
                placeholder: str = "{"+f"{value_path}:{funcs}"+"}"
                self.shared.logger.log(f"@StringFormats.format > Handling {placeholder} placeholder.", "NP_DEBUG")

                # getting path value
                try:
                    value: typing.Any =  ast.literal_eval(("{"+value_path+"}").format(**kwargs))
                except:
                    value: str = ("{"+value_path+"}").format(**kwargs)

                self.shared.logger.log(f"@StringFormats.format > Got {placeholder}'s value {value}.", "NP_DEBUG")
                
                # if the value is dict > formatting both key and value
                if isinstance(value, dict):
                    self.shared.logger.log(f"@StringFormats.format > Detected dictionary as value.", "NP_DEBUG")
                    # both key and values must exist
                    keys = tuple(value.keys())
                    values = tuple(value.values())

                    if not keys or not values:
                        self.shared.logger.log(f"@StringFormats.format > Missing keys or values, ignoring.", "NP_DEBUG")
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

        except Exception as error:
            self.shared.logger.log( f"@StringFormats.format > {type(error).__name__}: {error}", "ERROR")
        return