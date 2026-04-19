from services.rag_service import ingest_seed_knowledge_base


def main() -> None:
    chunks = ingest_seed_knowledge_base()
    print(f"Ingested {chunks} chunks into Chroma knowledge base.")


if __name__ == "__main__":
    main()
