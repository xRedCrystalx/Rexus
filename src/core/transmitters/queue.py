import sys, typing, asyncio
sys.dont_write_bytecode = True
import src.connector as con

class QueueSystem:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared

    async def _thread_event_runner(self, funcs: tuple[typing.Callable], guild_id: int, **kwargs) -> None:        
        guild_database: dict = self.shared.db.load_data(guild_id)
        bot_database: dict[str, typing.Any] = self.shared.db.load_data()
        self.shared.logger.log(f"@QueueSystem._thread_event_runner > Recieved task for execution. Loaded guild's and bot's database into the memory.", "NP_DEBUG")

        try:
            tasks: list[asyncio.Task] = [self.shared.loop.create_task(func(guild_id=guild_id, guild_db=guild_database, bot_db=bot_database, **kwargs), name=func.__qualname__) for func in funcs]
            self.shared.logger.log(f"@QueueSystem._thread_event_runner > Created list of task functions.", "NP_DEBUG")
            
            done: set[asyncio.Task]
            pending: set[asyncio.Task]

            done, pending = await asyncio.wait(tasks, timeout=.1)
            self.shared.logger.log(f"@QueueSystem._thread_event_runner > Execution completed. Returning completed and incompleted functions.", "NP_DEBUG")

            for task in [*done, *pending]:
                if not task.done():
                    task.cancel("Forcefully cancelled task.")
                    await asyncio.sleep(0)
                try:
                    result: list[dict] = await task
                    if result:
                        self.shared.logger.log(f"@QueueSystem._thread_event_runner > Sending task data to Sender.resolver", "NP_DEBUG")
                        self.shared.sender.resolver(result)

                except (asyncio.CancelledError, asyncio.InvalidStateError, asyncio.TimeoutError):
                    self.shared.logger.log(f"@QueueSystem.Task.{task.get_name()} ({guild_id}): Task killed.", "WARNING")
                except Exception as error:
                    self.shared.logger.log(f"@QueueSystem.Task.{task.get_name()} ({guild_id}): {type(error).__name__}: {error}", "ERROR")
            
            self.shared.logger.log(f"@QueueSystem._thread_event_runner > Completed main Task. Success rate: {len(done)}/{len(pending)+len(done)}", "SYSTEM")

        except ExceptionGroup as groupError:
            self.shared.logger.log(f"@QueueSystem._thread_event_runner ({guild_id}): Exception Group: {', '.join([f'SubE {num}: {exception}' for num, exception in enumerate(groupError.exceptions, 1)])}", "ERROR")
        except Exception as error:
            self.shared.logger.log(f"@QueueSystem._thread_event_runner ({guild_id}): {type(error).__name__}: {error}", "ERROR")
        return None

    async def add_to_queue(self, event: str, guild_id: int, **kwargs) -> None:
        self.shared.logger.log(f"@QueueSystem.add_to_queue > Recieved {event} event.", "NP_DEBUG")
        functions: tuple[typing.Callable] | None = self.filter.get(event)

        if functions:
            try:
                self.shared.loop.create_task(self._thread_event_runner(guild_id=guild_id, funcs=functions, **kwargs))
                self.shared.logger.log(f"@QueueSystem.add_to_queue > Successfully created task for {event} event.", "SYSTEM")
            except Exception as error:
                self.shared.logger.log(f"@QueueSystem.add_to_queue: {type(error).__name__}: {error}", "ERROR")
        return None

    def reload_filters(self) -> None:
        self.filter: dict[str, tuple[typing.Callable]] = {
            "on_message" : (self.shared.AI.ask_ai, self.shared.ping_prot.find_pings, self.shared.auto_slowmode.message_listener, self.shared.message_handlers.fan_art,
                            self.shared.message_handlers.responder, self.shared.message_handlers.simon_invite_link_detection, self.shared.message_handlers.antilink,
                            self.shared.auto_deleter.add_to_queue, self.shared.spy.queue),
            "on_message_edit" : (self.shared.ping_prot.find_pings, self.shared.message_handlers.antilink, self.shared.message_handlers.simon_invite_link_detection,
                                self.shared.spy.queue),
            "on_automod_action" : (self.shared.miscellaneous.automod_response, ),
            "on_member_join" : (self.shared.imper_detection.detection_on_join, ),
            "on_member_update" : (self.shared.imper_detection.detection_on_update, ),
            "on_raw_reaction_add" : (self.shared.reaction_filter.check_reaction, ),
            "on_voice_state_update" : ()
        }
        self.shared.logger.log(f"@QueueSystem.reload_filters > Filters reloaded.", "NP_DEBUG")

