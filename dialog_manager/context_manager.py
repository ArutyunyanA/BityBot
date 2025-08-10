from dialog_manager.context import DialogContext
from core.interpreter import Interpreter
from core.actions import ActionHandler
from core.parser import ParserNLP
import asyncio

class DialogManager:

    def __init__ (self):
        self.context = DialogContext()
        self.interpreter = Interpreter()
        self.actions = ActionHandler()
        self.parser = ParserNLP()

    async def process(self, user_input: str):
        ctx = self.context
        if ctx.expecting_input and ctx.waiting_for_slot:
            ctx.slots[ctx.waiting_for_slot] = user_input
            ctx.expecting_input = False
            ctx.waiting_for_slot = None
            return await self.execute_current_intent(user_input)
        intent = self.interpreter.get_intent(user_input)
        if not intent:
            return "Sorry, I did not understand that."
        ctx.current_intent = intent
        ctx.slots = {}
        ctx.expecting_input = False

        for action in intent.get("actions", []):
            match action:
                case {"ask": question}:
                    print(f"Question: {question}")
                    if "slots" in intent:
                        slot_name = intent["slots"] if isinstance(intent["slots"], str) else intent["slots"][0]
                    else:
                        slot_name = "input"
                    ctx.expecting_input = True
                    ctx.waiting_for_slot = slot_name
                    return question
                case {"file_select": _}:
                    ctx.expecting_input = True
                    ctx.waiting_for_slot = "filename"
                    return "Please provide the file name."
                case {"parser_input": parser_data} if isinstance(parser_data, dict):
                    method = parser_data.get("method", "nlp")
                    structure = parser_data.get("structure", [])
                    print(f"[DEBUG] Parsing with method: {method}, structure: {structure}")
                    parsed = await self.parser.parse(user_input, method, structure)
                    ctx.slots.update(parsed)
                case {"register_current_resource": _}:
                    await ctx.register_current_resource(
                        filename=ctx.slots.get("filename"),
                        file_type=ctx.slots.get("file_type")
                    )
                case {"inject_current_file": _}:
                    await ctx.inject_current_file()
                case {"run": run_data}:
                    if ctx.current_file and "filename" not in ctx.slots:
                        ctx.slots["filename"] = ctx.current_file
                    return await self.actions.execute(
                        module_name=run_data["module"],
                        function_name=run_data["function"],
                        **ctx.slots
                    )
                case {"respond": response}:
                    return response
                case _:
                    continue
        return "Done!"

    async def execute_current_intent(self, user_input: str):
        ctx = self.context
        for action in ctx.current_intent.get("actions", []):
            match action:
                case {"parser_input": parser_data} if isinstance(parser_data, dict):
                    method = parser_data.get("method", "nlp")
                    structure = parser_data.get("structure", [])
                    print(f"[DEBUG] Parsing with method: {method}, structure: {structure}")
                    parsed = await self.parser.parse(user_input, method, structure)
                    ctx.slots.update(parsed)
                case {"register_current_resource": rc}:
                    file_type = rc.get("file_type") if isinstance(rc, dict) else ctx.slots.get("file_type")
                    await ctx.register_current_resource(filename=ctx.slots.get("filename"), file_type=file_type)
                case {"inject_current_file": _}:
                    await ctx.inject_current_file()
                case {"run": run_data}:
                    print(f"[DEBUG] Current file: {ctx.current_file}")
                    print(f"[DEBUG] Current slots: {ctx.slots}")
                    if ctx.current_file and "filename" not in ctx.slots:
                        ctx.slots["filename"] = ctx.current_file
                    return await self.actions.execute(
                        run_data["module"],
                        run_data["function"],
                        **ctx.slots
                    )
                case {"respond": response}:
                    return response
        return "Finish current intent"
