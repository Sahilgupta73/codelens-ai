from functools import lru_cache
from transformers import AutoTokenizer


@lru_cache(maxsize=1)
def get_tokenizer():
    return AutoTokenizer.from_pretrained(
        "sentence-transformers/all-MiniLM-L6-v2",
        use_fast=True,
    )


def chunk_documents(
    documents: list[dict],
    chunk_size: int = 220,
    overlap: int = 30,
) -> list[dict]:
    """Create token-based chunks with original source locations."""

    if not 1 <= chunk_size <= 220:
        raise ValueError("chunk_size must be between 1 and 220.")

    if not 0 <= overlap < chunk_size:
        raise ValueError("overlap must be smaller than chunk_size.")

    tokenizer = get_tokenizer()
    chunks = []

    for document in documents:
        text = document["content"]

        encoded = tokenizer(
            text,
            add_special_tokens=False,
            return_offsets_mapping=True,
            truncation=False,
            verbose=False,
        )

        offsets = encoded["offset_mapping"]
        step = chunk_size - overlap

        for start in range(0, len(offsets), step):
            end = min(start + chunk_size, len(offsets))

            char_start = offsets[start][0]
            char_end = offsets[end - 1][1]
            content = text[char_start:char_end]

            if content.strip():
                # Check the actual substring before embedding it.
                token_count = len(tokenizer.encode(content))

                if token_count > 256:
                    raise ValueError(
                        f"Chunk too long in {document['file_path']}"
                    )

                chunks.append({
                    "file_path": document["file_path"],
                    "start_line": text.count("\n", 0, char_start) + 1,
                    "end_line": text.count("\n", 0, char_end - 1) + 1,
                    "content": content,
                })

            if end == len(offsets):
                break

    return chunks