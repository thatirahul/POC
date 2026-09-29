from app.services.embedding_service import EmbeddingService
from app.services.hana_vector_service import HanaVectorService


def main():

    print("=" * 60)
    print("HANA VECTOR SEARCH TEST")
    print("=" * 60)

    question = "What is SAP CAP?"

    embedding_service = EmbeddingService()
    vector_service = HanaVectorService()

    try:

        print("\nQuestion:")
        print(question)

        print("\nGenerating query embedding...")

        query_embedding = (
            embedding_service.generate_query_embedding(
                question
            )
        )

        print("Query embedding generated.")
        print(
            f"Vector dimension: {len(query_embedding)}"
        )

        print("\nSearching HANA...")

        results = vector_service.search_similar_chunks(
            query_embedding=query_embedding,
            top_k=5,
        )

        print(
            f"\nRetrieved {len(results)} chunks:\n"
        )

        for index, result in enumerate(results, start=1):

            print(f"--- Result {index} ---")
            print(
                f"Score: {result['score']:.4f}"
            )
            print(
                f"Document: {result['document_id']}"
            )
            print(
                f"Chunk: {result['chunk_index']}"
            )
            print(
                f"Text: {result['chunk_text']}"
            )
            print()

    finally:

        embedding_service.close()
        vector_service.close()


if __name__ == "__main__":
    main()