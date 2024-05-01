import sys, typing, dataclasses
sys.dont_write_bytecode = True


@dataclasses.dataclass
class Event:
    event_obj: typing.Callable
    action: str
    event_data: dict[str, typing.Any]
    _async: bool = True

    @classmethod
    def create_event(cls, event_obj: typing.Callable, action: str, event_data: dict[str, typing.Any], _async: bool = True) -> "Event":
        return Event(event_obj=event_obj, action=action, event_data=event_data, _async=_async)
