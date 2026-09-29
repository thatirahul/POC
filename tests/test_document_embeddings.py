from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService

PDF_PATH = "documents/sap_cap.pdf"


def main():

    print("=" * 70)
    print("DOCUMENT → CHUNKS → EMBEDDINGS")
    print("=" * 70)

    document_service = DocumentService()
    embeddings = EmbeddingService()

    # -----------------------------------------------------
    # Load PDF and create chunks
    # -----------------------------------------------------

    print("\nLoading document...")

    chunks = document_service.process_document(
        PDF_PATH
    )

    print(
        f"Total chunks created: {len(chunks)}"
    )

    # -----------------------------------------------------
    # Generate embeddings
    # -----------------------------------------------------

    print("\nGenerating embeddings...")

    texts = [
        chunk.page_content
        for chunk in chunks
    ]

    vectors = [
    embeddings.generate_document_embedding(text)
    for text in texts
]

    # -----------------------------------------------------
    # Display results
    # -----------------------------------------------------

    for index, vector in enumerate(vectors):

        print(
            f"\nChunk {index + 1}"
        )

        print(
            "Text length:",
            len(texts[index])
        )

        print(
            "Vector dimension:",
            len(vector)
        )

        print(
            "First 5 values:",
            vector[:5]
        )

    print("\n" + "=" * 70)
    print("DOCUMENT EMBEDDING SUCCESSFUL")
    print("=" * 70)


if __name__ == "__main__":
    main()