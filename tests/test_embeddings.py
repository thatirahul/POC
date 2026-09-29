# from app.services.embedding_service import AICoreEmbeddings


# def main():

#     print("=" * 70)
#     print("SAP AI CORE EMBEDDING TEST")
#     print("=" * 70)

#     embeddings = AICoreEmbeddings()

#     text = """
#     SAP CAP is the SAP Cloud Application Programming Model.
#     SAP CAP can be used to build enterprise applications
#     on SAP Business Technology Platform.
#     """

#     print("\nInput text:")
#     print(text)

#     print("\nGenerating embedding...")

#     vector = embeddings.embed_query(text)

#     print("\nEmbedding generated successfully!")

#     print(
#         "\nVector dimension:",
#         len(vector)
#     )

#     print(
#         "\nFirst 10 vector values:"
#     )

#     print(vector[:10])

#     print("\n" + "=" * 70)
#     print("EMBEDDING TEST SUCCESSFUL")
#     print("=" * 70)


# if __name__ == "__main__":
#     main()

from app.services.embedding_service import EmbeddingService


def main():
    print("=" * 70)
    print("SAP HANA NATIVE EMBEDDING TEST")
    print("=" * 70)

    text = """
    SAP CAP is the SAP Cloud Application Programming Model.
    SAP CAP can be used to build enterprise applications
    on SAP Business Technology Platform.
    """

    service = EmbeddingService()

    print("\nGenerating document embedding...\n")

    embedding = service.generate_document_embedding(text)

    print("Embedding generated successfully!")
    print("Model:", service.MODEL_NAME)
    print("Vector dimension:", len(embedding))
    print("\nFirst 10 values:")
    print(embedding[:10])

    service.close()


if __name__ == "__main__":
    main()