import sys, typing, asyncio
sys.dont_write_bytecode = True
import src.connector as con

class Reloader:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared

    def _resolver(self, keyword: str) -> str:
        """Basic resolver for special input"""
        if keyword == "*":
            for module in self.config:
                self.reload_module(module)
        else:
            return keyword

    def load_configuration(self) -> dict[str, dict[str, str | list[str] | dict]]:
        """Basic json config loading for dynamic updates."""
        self.shared.logger.log(f"@Reloader.load_configuration > Getting configuration..", "NP_DEBUG")
        return self.shared.db.load_data().get("reloader")

    def stop_task(self, module: str) -> None:
        """Attempts to find running inf. `asyncio.Task[module.start]` and kills it."""
        self.shared.logger.log(f"@Reloader.stop_task > Checking for active task.", "NP_DEBUG")
        for task in self.shared.plugin_tasks:
            if task.get_name().startswith(module):
                self.shared.logger.log(f"@Reloader.stop_task > Found task. Terminating", "NP_DEBUG")
                if task.cancel():
                    self.shared.logger.log(f"@Reloader.stop_task > Task terminated.", "NP_DEBUG")
                    try:
                        task.result()
                    except (asyncio.CancelledError, asyncio.InvalidStateError):
                        pass
                    except Exception as error:
                        self.shared.logger.log(f"@Plugins.stop_tasks.Task.{task.get_name()}: {type(error).__name__}: {error}", "ERROR")
                
                self.shared.logger.log(f"@Reloader.stop_task > Removing task from the list.", "NP_DEBUG")
                self.shared.plugin_tasks.remove(task)
                return
        else:
            self.shared.logger.log(f"@Reloader.stop_task > Did not find any active task.", "NP_DEBUG")
        
    def start_task(self, module: typing.Callable) -> None:
        """Auto executes `main` methods and starts a new instance of `asyncio.Task[module.start]` if exist. After class initialization."""

        if module.__class__.__dict__.get("main"):
            module.main()
            self.shared.logger.log(f"@Reloader.start_task > Found and executed `main` function.", "NP_DEBUG")
        else:
            self.shared.logger.log(f"@Reloader.start_task > Did not find `main` function. Ignoring.", "NP_DEBUG")

        self.shared.logger.log(f"@Reloader.start_task > Checking for plugin functions.", "NP_DEBUG")
        if module.__class__.__dict__.get("start"):
            task: asyncio.Task = asyncio.get_running_loop().create_task(module.start(), name=module.start.__qualname__)
            self.shared.logger.log(f"@Reloader.start_task > Found and started `start` task.", "NP_DEBUG")

            self.shared.plugin_tasks.append(task)
            self.shared.logger.log(f"@Reloader.start_task > Added task to the list. {len(self.shared.plugin_tasks)}", "NP_DEBUG")
        else:
            self.shared.logger.log(f"@Reloader.start_task > Did not find `start` function. Ignoring.", "NP_DEBUG")

    def finish(self) -> None:
        """Finish reloading - updating required datatypes"""
        self.shared.logger.log(f"@Reloader.finish > Reloading filters.", "NP_DEBUG")
        self.shared.queue.reload_filters()

    def reload_module(self, module: str) -> bool:
        """
        Reloads module.\n
        Kills running tasks, saves important variables, removes and re-imports into the system, execute, start tasks and updates variables with data.
        Config: config.json[reloader]

        Arguments:
        - module: `str` > name of Module
        """
        self.shared.logger.log(f"@Reloader.module > Re-loading {module}", "NP_DEBUG")
        self.config = self.load_configuration()

        # resolver check
        if not (module := self._resolver(module)):
            return

        # load updated configuration
        if not (config := self.config.get(module)):
            return self.shared.logger.log(f"@Reloader.reload_module > Failed to load configuration for {module}.", "ERROR")

        # stop running tasks
        self.stop_task(module)

        # save important RAM db
        old_data: dict = {}
        for var in config["save"]:
            old_data[var] = getattr(getattr(self.shared, config["var"]), var)
        self.shared.logger.log(f"@Reloader.reload_module > Saved old variable data of a module: Len: {len(old_data.keys())}.", "NP_DEBUG")

        # get module name and remove it from system.modules (if it exists)
        if (path := config["path"]) in sys.modules:
            del sys.modules[path]
        self.shared.logger.log(f"@Reloader.reload_module > Removed module from sys.modules.", "NP_DEBUG")

        # import class from the path
        try:
            exec(f"from {path} import {module}")
            self.shared.logger.log(f"@Reloader.reload_module > Re-importing module.", "NP_DEBUG")
        except Exception as error:
            self.shared.logger.log(f"@Reloader.reload_module > {type(error).__name__}: {error}", "ERROR")

        # try to save variable and run class with arguments
        try:
            exec_module: typing.Callable = eval(module)
            setattr(self.shared, config["var"], exec_module := eval(f"{module}(**{config["kwargs"]})"))
            self.shared.logger.log(f"@Reloader.reload_module > Executed module and applied it to the shared object.", "NP_DEBUG")
            
            # apply saved data to updated class/module
            for var, data in old_data.items():
                setattr(getattr(self.shared, config["var"]), var, data)
            self.shared.logger.log(f"@Reloader.reload_module > Applied old data to reloaded module.", "NP_DEBUG")

            self.start_task(exec_module)
            self.finish()
            self.shared.logger.log(f"@Reloader.reload_module > Successfully reloaded {module}!", "SYSTEM")
            return True

        except Exception as error:
            self.shared.logger.log(f"@Reloader.reload_module > {type(error).__name__}: {error}", "ERROR")

    async def reload_discord_module(self, path: str) -> None:
        self.shared.logger.log(f"@Reloader.reload_discord_module > Attempting to reload discord module: {path}.", "NP_DEBUG")
        try:
            await self.shared.bot.reload_extension(path)
            self.shared.logger.log(f"@Reloader.reload_discord_module > Successfully reloaded {path}!", "SYSTEM")
        except Exception as error:
            self.shared.logger.log(f"@Reloader.reload_discord_module > {type(error).__name__}: {error}", "ERROR")

