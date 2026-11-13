import os
from pathlib import Path

SKIP_FOLDERS = {
    ".venv", "venv", ".git", "__pycache__",
    ".pytest_cache", "node_modules", "chroma_db",
}

ALLOWED_EXTENSIONS = {".py", ".md"}
ALLOWED_FILENAMES = {"requirements.txt", "pyproject.toml"}

MAX_FILE_SIZE = 500_000  # 500 KB


def load_repository(repo_path: str) -> list[dict]:
    """Read supported text files without executing any project code."""
    root = Path(repo_path).expanduser().resolve()

    if not root.is_dir():
        raise ValueError(f"Project folder does not exist: {root}")

    documents = []

    for current_folder, folders, files in os.walk(root):
        # Avoid environments, hidden folders, and directory links.
        folders[:] = sorted(
            folder
            for folder in folders
            if folder not in SKIP_FOLDERS
            and not folder.startswith(".")
            and not (Path(current_folder) / folder).is_symlink()
            and not (Path(current_folder) / folder).is_junction()
        )

        for filename in sorted(files):
            path = Path(current_folder) / filename

            if filename.startswith(".") or path.is_symlink():
                continue

            if (
                path.suffix.lower() not in ALLOWED_EXTENSIONS
                and filename not in ALLOWED_FILENAMES
            ):
                continue

            try:
                resolved_path = path.resolve()

                if not resolved_path.is_relative_to(root):
                    continue

                if path.stat().st_size > MAX_FILE_SIZE:
                    continue

                content = path.read_text(encoding="utf-8")

            except (OSError, UnicodeError) as error:
                print(f"Skipped {path.name}: {type(error).__name__}")
                continue
                    
            if not content.strip():
                continue

            documents.append({
                "file_path": path.relative_to(root).as_posix(),
                "content": content,
                "line_count": len(content.splitlines()),
            })

    return documents