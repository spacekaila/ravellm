from src.embeddings import PatternEmbedder
from src.vector_store import PatternVectorStore
import json


def main():

    with open("data/raw/patterns_0.json", "r") as file:
        patterns = json.load(file)

    print(f"Adding {len(patterns)} patterns to the vector store")

    embedder = PatternEmbedder()
    embeddings = embedder.embed_patterns(patterns=patterns)

    print(f"Embedding shape: {embeddings.shape}")

    vector_store = PatternVectorStore()
    vector_store.add_patterns(patterns=patterns, embeddings=embeddings)


if __name__ == "__main__":
    main()
