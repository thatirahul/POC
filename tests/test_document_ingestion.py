from pathlib import Path

from app.rag.loader import load_pdf
from app.rag.splitter import split_documents
from app.services.embedding_service import EmbeddingService
from app.services.hana_vector_service import HanaVectorService


def main():

    print("=" * 60)
    print("DOCUMENT INGESTION TEST")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. PDF path
    # ---------------------------------------------------------

    pdf_path = Path("documents/sap_cap.pdf")

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    # ---------------------------------------------------------
    # 2. Load PDF
    # ---------------------------------------------------------

    print("\nLoading PDF...")

    documents = load_pdf(str(pdf_path))

    print("PDF loaded successfully.")
    print(f"Pages loaded: {len(documents)}")

    # ---------------------------------------------------------
    # 3. Split documents into chunks
    # ---------------------------------------------------------

    print("\nSplitting document into chunks...")

    chunks = split_documents(documents)

    print("Document splitting completed.")
    print(f"Total chunks: {len(chunks)}")

    if not chunks:
        raise RuntimeError(
            "No chunks were generated from the PDF."
        )

    # ---------------------------------------------------------
    # 4. Create services
    # ---------------------------------------------------------

    embedding_service = EmbeddingService()
    vector_service = HanaVectorService()

    document_id = pdf_path.stem

    try:

        # -----------------------------------------------------
        # 5. Generate embeddings and store chunks
        # -----------------------------------------------------

        print("\nStarting chunk ingestion...")
        print("-" * 60)

        for index, chunk in enumerate(chunks):

            chunk_text = chunk.page_content.strip()

            if not chunk_text:
                print(
                    f"Skipping chunk {index}: empty text"
                )
                continue

            chunk_id = (
                f"{document_id}-chunk-{index}"
            )

            print(
                f"\nProcessing chunk "
                f"{index + 1}/{len(chunks)}..."
            )

            print(
                f"Characters: {len(chunk_text)}"
            )

            # Generate SAP HANA native embedding
            embedding = (
                embedding_service
                .generate_document_embedding(
                    chunk_text
                )
            )

            print(
                f"Embedding generated: "
                f"{len(embedding)} dimensions"
            )

            # Store chunk + embedding in HANA
            vector_service.insert_chunk(
                chunk_id=chunk_id,
                document_id=document_id,
                chunk_index=index,
                chunk_text=chunk_text,
                embedding=embedding,
            )

            print("Stored successfully.")

        # -----------------------------------------------------
        # 6. Completed
        # -----------------------------------------------------

        print("\n" + "=" * 60)
        print("DOCUMENT INGESTION COMPLETED")
        print("=" * 60)

        print(f"Document: {pdf_path.name}")
        print(f"Pages: {len(documents)}")
        print(f"Chunks processed: {len(chunks)}")
        print("Embeddings: SAP_NEB.20240715")
        print("Vector dimension: 768")
        print("Storage: RAG_DOCUMENT_CHUNKS")

    finally:

        embedding_service.close()
        vector_service.close()


if __name__ == "__main__":
    main()