from app.services.rag_service import RAGService


def main():

    print("=" * 60)
    print("END-TO-END RAG TEST")
    print("=" * 60)

    # --------------------------------------------------
    # Select the document to search
    # --------------------------------------------------

    document_id = "sap_cap"

    # --------------------------------------------------
    # Ask a question
    # --------------------------------------------------

    question = "What is SAP CAP?"

    print(f"\nDocument ID:\n{document_id}")

    print(f"\nQuestion:\n{question}")

    # --------------------------------------------------
    # Create RAG service
    # --------------------------------------------------

    rag_service = RAGService()

    try:

        # --------------------------------------------------
        # Generate answer using only this document
        # --------------------------------------------------

        answer = rag_service.generate_answer(
            question=question,
            top_k=5,
            document_id=document_id,
        )

        print("\n" + "=" * 60)
        print("FINAL AI ANSWER")
        print("=" * 60)

        print(answer)

    finally:

        # --------------------------------------------------
        # Close connections
        # --------------------------------------------------

        rag_service.close()


if __name__ == "__main__":
    main()