import chromadb
from chromadb.config import Settings
import json


class PatternVectorStore:
    def __init__(self, persist_directory="./data/processed"):
        self.client = chromadb.PersistentClient(path=persist_directory, settings=Settings())

        # create or get collection
        self.collection = self.client.get_or_create_collection(
            name="knitting_patterns",
            metadata={"description": "Ravelry knitting patterns"}
        )

    def _pattern_to_text(self, pattern):
        """Convert pattern to searchable text"""
        return f"{pattern["name"]} by {pattern["designer"]} - {pattern["category"]}"

    def _pattern_to_metadata(self, pattern):
        """Extract metadata for filtering"""
        return {
            "name": pattern["name"],
            "designer": pattern["designer"],
            "category": pattern["category"],
            "yarn_weight": pattern["yarn_weight"],
            "difficulty": pattern["difficulty"],
            "notes": pattern["notes"],
            "url": pattern["url"],
            "downloadable": pattern["downloadable"],
            "free": pattern["free"]
        }

    def add_patterns(self, patterns, embeddings):
        """Add patterns to vector database

        Parameters
        ----------
        patterns : list of dicts
            pattern information
        embeddings : array
            pattern embeddings
        """
        ids = [str(p["id"]) for p in patterns]
        documents = [self._pattern_to_text(p) for p in patterns]
        metadatas = [self._pattern_to_metadata(p) for p in patterns]

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadatas
        )

        print(f"Added {len(patterns)} patterns to vector store")

    def search(self, query_embedding, n_results=5, filter_dict=None):
        """Search for similar patterns"""
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            where=filter_dict
        )

        return results


def main():
    from embeddings import PatternEmbedder

    with open("data/raw/patterns.json", "r") as f:
        patterns = json.load(f)

    embedder = PatternEmbedder()
    embeddings = embedder.embed_patterns(patterns)

    print(f"Embedding shape: {embeddings.shape}")

    vector_store = PatternVectorStore()
    vector_store.add_patterns(patterns=patterns, embeddings=embeddings)

    query = "chunky cardigan for fall"
    query_embedding = embedder.model.encode(query)
    results = vector_store.search(query_embedding, n_results=2)
    print(f"Search results: {results}")


if __name__ == "__main__":
    main()
