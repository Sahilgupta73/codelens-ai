from pathlib import Path

from src.indexer import index_repository


project_path = Path(__file__).resolve().parent

print("Indexing project...")
store, file_count, chunk_count = index_repository(
    str(project_path)
)

print(f"\nIndexed {file_count} files into {chunk_count} chunks.")

question = input("\nAsk a question about your code: ").strip()

if question:
    results = store.similarity_search(question, k=3)

    for number, document in enumerate(results, start=1):
        metadata = document.metadata

        print(f"\n--- Result {number} ---")
        print(f"File: {metadata['file_path']}")
        print(
            f"Lines: {metadata['start_line']}"
            f"–{metadata['end_line']}"
        )
        print(document.page_content)
else:
    print("No question entered.")