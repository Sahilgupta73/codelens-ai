from pathlib import Path

from src.rag import answer_question


project_path = Path(__file__).resolve().parent

print("CodeLens AI — Ask your codebase")
print("Type 'exit' to stop.")

while True:
    question = input("\nYou: ").strip()

    if question.lower() in {"exit", "quit"}:
        break

    if not question:
        continue

    result = answer_question(
        repo_path=str(project_path),
        question=question,
    )

    print("\nCodeLens AI:")
    print(result["answer"])

    if result["sources"]:
        print("\nRetrieved sources:")

        for number, source in enumerate(result["sources"], start=1):
            print(f"[Source {number}] {source}")