from pathlib import Path

from src.loader import load_repository
from src.chunker import chunk_documents

project_path = Path(__file__).resolve().parent

documents = load_repository(str(project_path))
chunks = chunk_documents(documents)

print(f"Loaded files: {len(documents)}")
print(f"Created chunks: {len(chunks)}")

for number, chunk in enumerate(chunks[:5], start=1):
    print(f"\n--- Chunk {number} ---")
    print(f"File: {chunk['file_path']}")
    print(f"Lines: {chunk['start_line']}–{chunk['end_line']}")
    print(chunk["content"])