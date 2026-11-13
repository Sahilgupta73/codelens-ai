from pathlib import Path
from src.loader import load_repository

# Read this project's files as our first example.
project_path = Path(__file__).resolve().parent

documents = load_repository(str(project_path))

print(f"\nLoaded {len(documents)} files:\n")

for document in documents:
    print(
        f"{document['file_path']} "
        f"— {document['line_count']} lines"
    )