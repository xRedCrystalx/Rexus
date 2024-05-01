import sys, typing, dataclasses
sys.dont_write_bytecode = True

@dataclasses.dataclass
class Event:
    event_obj: typing.Callable
    action: str
    event_data: dict[str, typing.Any]
    _async: bool = True
