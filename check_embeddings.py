from src.embeddings import get_embedding_model

print("Loading embedding model...")
model = get_embedding_model()

examples = [
    "Load an API key from an environment variable.",
    "Split source code into smaller chunks.",
    "Calculate the total price of a shopping cart.",
]

# Convert the example documents into vectors.
document_vectors = model.embed_documents(examples)

# Convert a search question into a vector.
question = "How do I read my API key?"
question_vector = model.embed_query(question)

print(f"\nDocuments embedded: {len(document_vectors)}")
print(f"Numbers per vector: {len(question_vector)}")

# For normalized vectors, the dot product is cosine similarity.
scores = [
    sum(q * d for q, d in zip(question_vector, vector))
    for vector in document_vectors
]

print("\nResults, ordered by similarity:")

for score, text in sorted(
    zip(scores, examples),
    key=lambda item: item[0],
    reverse=True,
):
    print(f"{score:.3f} | {text}")