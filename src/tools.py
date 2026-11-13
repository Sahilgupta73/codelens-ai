from langchain_core.tools import tool

from src.loader import load_repository
from src.indexer import get_vector_store


def build_tools(repo_path: str):
    # Only expose files accepted by our repository loader.
    documents = load_repository(repo_path)
    files = {
        document["file_path"]: document["content"]
        for document in documents
    }

    store = get_vector_store(repo_path)

    @tool
    def list_files() -> str:
        """List supported repository files, including dependency files."""
        names = sorted(files)
        result = "\n".join(names[:100])
        if len(names) > 100:
            result += "\n[Only the first 100 files are shown.]"
        return (
            "PARTIAL FILE INVENTORY: Only supported, non-empty files "
            "accepted by the repository loader are listed. "
            "Hidden files such as .env, unsupported file types, "
            "and excluded folders are not inspected. "
            "This list cannot prove that configuration is absent "
            "from the entire project.\n\n"
            + (result or "No supported files found.")
        )

    @tool
    def search_code(query: str) -> str:
        """Search indexed code by meaning using a short search query."""
        results = store.similarity_search(query[:500], k=2)

        if not results:
            return "No indexed code found. Refresh the project index."

        sections = []

        for document in results:
            metadata = document.metadata

            sections.append(
                f"{metadata['file_path']}:"
                f"{metadata['start_line']}-{metadata['end_line']}\n"
                f"{document.page_content}"
            )

        return "\n\n".join(sections)

    @tool
    def read_file(
        file_path: str,
        start_line: int = 1,
        end_line: int = 40,
    ) -> str:
        """Read up to 40 lines from a supported file using its relative path."""
        normalized_path = file_path.replace("\\", "/")

        if normalized_path not in files:
            return "File unavailable. Use list_files for valid paths."

        lines = files[normalized_path].splitlines()

        if start_line < 1 or start_line > len(lines):
            return f"start_line must be between 1 and {len(lines)}."

        if end_line < start_line:
            return "end_line must be greater than or equal to start_line."

        end = min(end_line, start_line + 39, len(lines))

        numbered_lines = [
            f"{number}: {lines[number - 1]}"
            for number in range(start_line, end + 1)
        ]

        # Bound the returned text even when a source line is very long.
        output = "\n".join(numbered_lines)
        if len(output) > 4000:
            output = output[:4000] + "\n[Output truncated.]"

        return f"File: {normalized_path}\n{output}"

    return [list_files, search_code, read_file]