
import json
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

CATALOG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "shl_catalog.json")
EMBED_MODEL = "all-MiniLM-L6-v2"   # fast, small, good quality


class CatalogRetriever:
    def __init__(self):
        self.model = SentenceTransformer(EMBED_MODEL)
        self.catalog: list[dict] = []
        self.index: faiss.IndexFlatL2 | None = None
        self._load()

    def _load(self):
        """Catalog JSON load karo aur FAISS index banao."""
        catalog_path = os.path.abspath(CATALOG_PATH)

        if not os.path.exists(catalog_path):
            raise FileNotFoundError(
                f"Catalog not found at {catalog_path}. "
                "Run: python scraper/fallback_catalog.py"
            )

        with open(catalog_path, "r", encoding="utf-8") as f:
            self.catalog = json.load(f)

        if not self.catalog:
            raise ValueError("Catalog is empty!")

       
        texts = []
        for item in self.catalog:
            parts = [
                item.get("name", ""),
                item.get("description", ""),
                "Test type: " + item.get("test_type", ""),
                "Job levels: " + ", ".join(item.get("job_levels", [])),
                "Languages: " + ", ".join(item.get("languages", [])),
            ]
            texts.append(" | ".join(filter(None, parts)))

        # Embeddings banao
        embeddings = self.model.encode(texts, show_progress_bar=False)
        embeddings = np.array(embeddings).astype("float32")

        # FAISS index 
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

        print(f"[Retriever] Loaded {len(self.catalog)} assessments into FAISS index.")

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        """
        Query se most relevant assessments return karta hai.
        Returns list of assessment dicts with 'score' field added.
        """
        if not self.index or not self.catalog:
            return []

        query_vec = self.model.encode([query], show_progress_bar=False)
        query_vec = np.array(query_vec).astype("float32")

        distances, indices = self.index.search(query_vec, min(top_k, len(self.catalog)))

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.catalog):
                continue
            item = dict(self.catalog[idx])
            item["_score"] = float(dist)
            results.append(item)

        return results

    def get_all(self) -> list[dict]:
        """Saara catalog return karo (comparison/scope check ke liye)."""
        return self.catalog

    def get_by_name(self, name: str) -> dict | None:
        """Exact name se assessment dhundo."""
        name_lower = name.lower()
        for item in self.catalog:
            if item.get("name", "").lower() == name_lower:
                return item
        # Partial match
        for item in self.catalog:
            if name_lower in item.get("name", "").lower():
                return item
        return None

    def get_valid_urls(self) -> set[str]:
        """All valid catalog URLs ka set return karo."""
        return {item["url"] for item in self.catalog if item.get("url")}


# Singleton - load one time and use everytime
_retriever: CatalogRetriever | None = None


def get_retriever() -> CatalogRetriever:
    global _retriever
    if _retriever is None:
        _retriever = CatalogRetriever()
    return _retriever
