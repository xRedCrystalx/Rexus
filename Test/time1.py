import typing

def custom_format(string: str, **kwargs) -> str:
    def handle_list_format(value, format_indicator):
        if format_indicator == "comma":
            return ", ".join(map(str, value))
        elif format_indicator == "point":
            return "\n".join(["- " + str(item) for item in value])
        else:
            return ", ".join(map(str, value))

    def replace_placeholders(string: str, data: dict[str, typing.Any], path: str) -> str:
        for key, value in data.items():
            current_path: str = f"{path}.{key}"
            if isinstance(value, dict):
                string = replace_placeholders(string, value, current_path)
            elif isinstance(value, list):
                for match in (" | point", " | comma"):
                    string = string.replace("{" + f"{current_path}{match}" + "}", handle_list_format(value, match.split("|")[-1].strip()))
            else:
                string = string.replace("{" + f"{current_path}" + "}", str(value))
        return string

    for key, value in kwargs.items():
        if isinstance(value, dict):
            string = replace_placeholders(string, value, key)
        elif isinstance(value, list):
            for match in (" | point"), " | comma":
                string = string.replace("{" + f"{key}{match}" + "}", handle_list_format(value, match.split("|")[-1].strip()))
        else:
            string = string.replace("{" + key + "}", str(value))
    
    return string

# Example usage
kwarg = {"var1": {"in1": 1, "in2": 2}, "var2": True, "var3": [1, 2, 3, 4, 5, 6, 7, 8, 9]}
string = "this is a {var2} string with {var1.in1} and {var1.in2} this list will be handled with commas: {var3 | comma}, this one will be pointed: {var3 | point}"

# Using custom_format to format the string with kwargs
formatted_message = custom_format(string, **kwarg)

# Printing the formatted message
print(formatted_message)