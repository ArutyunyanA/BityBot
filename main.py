from dialog_manager.context_manager import DialogManager
import asyncio

async def main():
    print("Bity bot is ready, type 'quit' or 'exit' to finish your conversation.")
    context_manager = DialogManager()
    while True:
        user_input = await asyncio.to_thread(lambda: input("You: ").strip())
        if user_input.lower() in ("quit", "exit"):
            print("Bye!")
            break
        response = await context_manager.process(user_input)
        print(f"Bity:\n{response}")

if __name__ == "__main__":
    asyncio.run(main())
