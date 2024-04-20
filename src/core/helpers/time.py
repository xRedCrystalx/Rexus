import sys, datetime, time, typing
sys.dont_write_bytecode = True
import src.connector as con

class TimeHelper:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared
        self.units: dict[str, int] = {
            "second": 1,
            "minute": 60,
            "hour": 3_600,
            "day": 86_400,
            "week": 604_800,
            "month": 2_592_000,
            "year": 31_104_000
        }

    def convert_to_seconds(self, value: int, option: typing.Literal["minute", "hour", "day", "week", "month", "year"]) -> int | float:
        if not (multiplicator := self.units.get(option)):
            return 0
        return value * multiplicator

    def seconds_to_string(self, seconds: int) -> str:
        components: list[str] = []

        for unit, value in self.units.items()[::-1]:
            if seconds >= value:
                count, seconds = divmod(seconds, value)
                components.append(f"{count} {unit}{"s" if count != 1 else ""}")

        return ", ".join(components) if components else "0 seconds"
    
    def string_to_seconds(self, time_string: str) -> int:
        total_seconds = 0
        components: map[str] = map(str.strip, time_string.split(","))
        
        for comp in components:
            count, unit = comp.split(" ")

            total_seconds += int(count) * self.units[unit.strip("s")]

        return total_seconds
    
    def current_timestamp(self) -> int:
        return int(time.time())
    
    def datetime(self, option: typing.Literal["UTC"] = None) -> datetime.datetime:
        if option == "UTC":
            return datetime.datetime.now(datetime.UTC)

        return datetime.datetime.now()


