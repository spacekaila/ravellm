from sentence_transformers import SentenceTransformer
import numpy as np
import json


class PatternEmbedder:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        """Initialize embedding model

        Parameters
        ----------
        model_name : str, optional
            LLM model, by default "all-MiniLM-L6-v2"
            which is lightweight (~80MB) and fast
        """

        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print("Model loaded successfully")

    def create_pattern_text(self, pattern: dict):
        """Convert pattern dict to text for embedding

        Parameters
        ----------
        pattern : dict
            pattern parameters
        """
        text_parts = [
            f"id: {pattern["id"]}",
            f"Pattern: {pattern["name"]}",
            f"Designer: {pattern["designer"]}",
            f"Category: {pattern["category"]}",
            f"Yarn weight: {pattern["yarn_weight"]}",
            f"Difficulty: {pattern["difficulty"]:.1f}/10",
        ]

        if pattern.get("notes"):
            text_parts.append(f"Description: {pattern["notes"]}")

        return " | ".join(text_parts)

    def embed_patterns(self, patterns):
        """Create embeddings for all patterns

        Parameters
        ----------
        patterns : list
            list of patterns
        """
        texts = [self.create_pattern_text(p) for p in patterns]

        print(f"Creating embeddings for {len(texts)} patterns...")
        embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True
        )

        return embeddings


def main():
    with open("data/raw/patterns.json", "r") as f:
        patterns = json.load(f)

    embedder = PatternEmbedder()
    embeddings = embedder.embed_patterns(patterns)

    print(f"Embedding shape: {embeddings.shape}")


if __name__ == "__main__":
    main()
