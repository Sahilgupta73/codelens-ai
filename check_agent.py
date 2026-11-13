from pathlib import Path

from langchain_core.messages import HumanMessage

from src.agent import build_debug_agent


project_path = Path(__file__).resolve().parent

print("Loading debugging agent...")
agent = build_debug_agent(str(project_path))

print("\nDescribe a problem or paste a traceback.")
print("For multiple lines, finish with a line containing only END.")

input_lines = []

while True:
    line = input()
    if line.strip() == "END":
        break
    input_lines.append(line)

question = "\n".join(input_lines).strip()

if not question:
    raise SystemExit("No question entered.")

for update in agent.stream(
    {
        "messages": [HumanMessage(content=question)],
        "tool_calls_used": 0,
    },
    config={"recursion_limit": 20},
    stream_mode="updates",
):
    for node_name, data in update.items():
        for message in data.get("messages", []):
            if node_name == "assistant":
                if message.tool_calls:
                    for call in message.tool_calls:
                        print(f"\n[Tool requested] {call['name']}")
                else:
                    print("\nCodeLens AI:")
                    print(message.content)

            elif node_name == "tools":
                print("[Tool result received]")