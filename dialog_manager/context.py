class DialogContext:

    def __init__(self):
        self.current_intent = None
        self.current_file = None
        self.current_file_type = None
        self.expecting_input = False
        self.waiting_for_slot = None
        self.slots = {}

    async def register_current_resource(self, filename: str, file_type: str):
        self.current_file = filename
        self.current_file_type = file_type
        print(f"[DEBUG] Register current file: {filename}, type: {file_type}")

    async def inject_current_file(self):
        if self.current_file and "filename" not in self.slots:
            self.slots["filename"] = self.current_file
            print(f"[DEBUG] Injected currentfile into slots: {self.current_file}")