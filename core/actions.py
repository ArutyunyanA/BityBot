import importlib
import asyncio
from inspect import signature
from services.excel_handler import ExcelHandler


class ActionHandler:

    def __init__(self):
        self.loaded_modules = {
            "actions": self,
            "excel_handler": ExcelHandler()
        }

    async def execute(self, module_name: str, function_name: str, **kwargs):
        if module_name not in self.loaded_modules:
            try:
                self.loaded_modules[module_name] = importlib.import_module(f"core.{module_name}")
            except ModuleNotFoundError:
                return f"[ERROR] Module '{module_name}' not found."

        module = self.loaded_modules[module_name]
        func = getattr(module, function_name, None)
        if not callable(func):
            return f"[ERROR] Function '{function_name}' not found in module '{module_name}'."

        try:
            params = list(signature(func).parameters.keys())
            arg_value = (
                kwargs[params[0]] if len(params) == 1 and params[0] in kwargs
                else {k: v for k, v in kwargs.items() if k in params}
            )

            print(f"[DEBUG] Calling {function_name} with: {arg_value}")
            match (asyncio.iscoroutinefunction(func), isinstance(arg_value, dict)):
                case (True, True):
                    result = await func(**arg_value)
                case (True, False):
                    result = await func(arg_value)
                case (False, True):
                    result = await asyncio.to_thread(func, **arg_value)
                case (False, False):
                    result = await asyncio.to_thread(func, arg_value) 
            return result

        except TypeError as err:
            return f"[ERROR] Argument mismatch for '{function_name}': {err}"
        except Exception as err:
            return f"[ERROR] Failed to execute function '{function_name}': {err}"




