import hashlib
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.loader import load_repository
from src.chunker import chunk_documents
from src.embeddings import get_embedding_model


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "chroma_db"


def get_vector_store(repo_path: str):
    root = Path(repo_path).resolve()

    # Give each repository its own collection.
    repo_id = hashlib.sha256(
        str(root).casefold().encode("utf-8")
    ).hexdigest()[:16]

    return Chroma(
        collection_name=f"code_{repo_id}",
        embedding_function=get_embedding_model(),
        persist_directory=str(DATABASE_PATH),
    )


def index_repository(repo_path: str):
    documents = load_repository(repo_path)
    chunks = chunk_documents(documents)

    if not chunks:
        raise ValueError("No supported, non-empty files were found.")

    records = [
        Document(
            page_content=chunk["content"],
            metadata={
                "file_path": chunk["file_path"],
                "start_line": chunk["start_line"],
                "end_line": chunk["end_line"],
            },
        )
        for chunk in chunks
    ]

    store = get_vector_store(repo_path)

    # Rebuild only this repository's generated index.
    # This does not change any source files.
    store.reset_collection()

    # Small batches also work when the repository grows.
    for start in range(0, len(records), 64):
        batch = records[start:start + 64]

        store.add_documents(
            documents=batch,
            ids=[
                f"chunk_{number}"
                for number in range(start, start + len(batch))
            ],
        )

    return store, len(documents), len(chunks)