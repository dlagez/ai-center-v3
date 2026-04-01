from src.api.deps import get_qdrant_store


if __name__ == "__main__":
    get_qdrant_store().ensure_collection()
    print("Qdrant collection initialized.")
