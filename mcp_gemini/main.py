import json
import re
from pathlib import Path
from task_manager import add_task, delete_task, list_tasks, clear_tasks
from llm_gemini import run_prompt

HISTORY_FILE = "chat_history.json"

def reset_history():
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)

def load_history():
    if Path(HISTORY_FILE).exists():
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def build_prompt_messages(history, tasks):
    messages = []

    # Only send system prompt once
    if not history:
        system_prompt = """
You are a helpful assistant managing the user's to-do list.

Reply in natural language, but always include an action tag at the beginning of your response using this format:

[ACTION:add|task name]
[ACTION:delete|task name]
[ACTION:list]
[ACTION:clear]
[ACTION:none]

Examples:
- [ACTION:add|buy milk] Got it, I've added that to your list.
- [ACTION:delete|call mom] Okay, I've removed that.
- [ACTION:list] Here are your current tasks:
- [ACTION:clear] I've cleared your to-do list.
- [ACTION:none] Just chatting? Cool 😎

If the user asks to see tasks, list them out in this format:
1. Task 1
2. Task 2
etc
""".strip()
        messages.append({"role": "system", "parts": [system_prompt]})

    # Always include the current tasks as context
    task_block = "\n".join(f"- {t}" for t in tasks) if tasks else "[No tasks]"
    messages.append({
        "role": "user",
        "parts": [f"Current tasks:\n{task_block}"]
    })

    # Add history of messages
    for turn in history:
        role = "user" if turn["role"] == "user" else "model"
        messages.append({"role": role, "parts": [turn["content"]]})

    return messages


def parse_action(response):
    match = re.match(r"\[ACTION:(\w+)(?:\|([^\]]+))?\]", response)
    if match:
        action = match.group(1)
        task = match.group(2) or ""
        message = response[match.end():].strip()
        return action.lower(), task.strip(), message
    return "none", "", response

def main():
    print("🤖 Gemini Task Manager")
    print("Type 'exit' or 'quit' to stop.\n")

    reset_history()
    history = []

    while True:
        user_input = input("> ").strip()
        if user_input.lower() in ("exit", "quit"):
            print("👋 Goodbye!")
            break

        history.append({"role": "user", "content": user_input})
        tasks = list_tasks()
        messages = build_prompt_messages(history, tasks)

        try:
            response = run_prompt(messages)
        except Exception as e:
            print(f"🤖 Error: {e}")
            continue

        history.append({"role": "model", "content": response})
        save_history(history)

        action, task, natural_reply = parse_action(response)
        print(f"🤖 {natural_reply}")

        if action == "add" and task:
            add_task(task)
        elif action == "delete" and task:
            delete_task(task)
        elif action == "clear":
            clear_tasks()
            print("🧹 Your to-do list has been cleared.")

if __name__ == "__main__":
    main()
