from typing import List, Dict, Any

from app.services.embedding_service import EmbeddingService
from app.services.hana_vector_service import HanaVectorService
from app.services.ai_core_service import AICoreService


class RAGService:
    """
    Handles the complete RAG flow:

    User Question
        ↓
    Query Embedding
        ↓
    HANA Vector Search
        ↓
    Relevant Document Chunks
        ↓
    Context Construction
        ↓
    SAP AI Core LLM
        ↓
    Final Answer
    """

    def __init__(self):

        self.embedding_service = EmbeddingService()
        self.vector_service = HanaVectorService()
        self.ai_core_service = AICoreService()

    # --------------------------------------------------
    # Retrieve relevant chunks
    # --------------------------------------------------

    def retrieve(
        self,
        question: str,
        top_k: int = 5,
        document_id: str | None = None,
    ) -> List[Dict[str, Any]]:

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        print("\nGenerating query embedding...")

        query_embedding = (
            self.embedding_service
            .generate_query_embedding(question)
        )

        print(
            f"Query embedding generated: "
            f"{len(query_embedding)} dimensions"
        )

        print("\nSearching HANA vector database...")

        if document_id:
            print(
                f"Searching only in document: "
                f"{document_id}"
            )
        else:
            print(
                "Searching across all documents..."
            )

        results = (
            self.vector_service
            .search_similar_chunks(
                query_embedding=query_embedding,
                top_k=top_k,
                document_id=document_id,
            )
        )

        print(
            f"Retrieved {len(results)} relevant chunks."
        )

        return results

    # --------------------------------------------------
    # Build context from retrieved chunks
    # --------------------------------------------------

    def build_context(
        self,
        results: List[Dict[str, Any]],
    ) -> str:

        if not results:
            return ""

        context_parts = []

        for index, result in enumerate(
            results,
            start=1,
        ):

            context_parts.append(
                f"""
--- Context {index} ---
Document: {result['document_id']}
Chunk: {result['chunk_index']}
Similarity Score: {result['score']:.4f}

{result['chunk_text']}
"""
            )

        return "\n".join(context_parts)

    # --------------------------------------------------
    # Generate final RAG answer
    # --------------------------------------------------

    def generate_answer(
        self,
        question: str,
        top_k: int = 5,
        document_id: str | None = None,
    ) -> str:

        # Step 1: Retrieve relevant chunks
        results = self.retrieve(
            question=question,
            top_k=top_k,
            document_id=document_id,
        )

        # Step 2: Handle no matching chunks
        if not results:
            return (
                "I could not find relevant information "
                "in the uploaded document."
            )

        # Step 3: Build document context
        context = self.build_context(results)

        # Step 4: Create prompt
        prompt = f"""
You are a document question-answering assistant.

Answer the user's question using ONLY the information
provided in the document context below.

If the answer is not available in the context,
say exactly:

"The information is not available in the uploaded document."

Do not use outside knowledge.
Do not invent or assume information.

Document Context:
{context}

User Question:
{question}

Answer:
"""

        print("\nSending context to SAP AI Core...")

        # SAP AI Core expects messages as a list of objects
        messages = [
            {
                "role": "user",
                "content": prompt,
            }
        ]

        # Step 5: Get final answer from SAP AI Core
        # AICoreService already returns only the answer string
        answer = (
            self.ai_core_service
            .generate_response(messages)
        )

        return answer

    # --------------------------------------------------
    # Close connections
    # --------------------------------------------------

    def close(self):

        self.embedding_service.close()
        self.vector_service.close()