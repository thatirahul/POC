from pathlib import Path

from langchain_core.documents import Document

from app.rag.loader import load_pdf
from app.rag.splitter import split_documents


class DocumentService:
    """
    Service responsible for loading documents and
    converting them into chunks for the RAG pipeline.
    """

    def __init__(self):
        pass

    # =========================================================
    # Load PDF
    # =========================================================

    def load_document(
        self,
        file_path: str,
    ) -> list[Document]:
        """
        Load a PDF document and return LangChain Documents.
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Document not found: {file_path}"
            )

        if path.suffix.lower() != ".pdf":
            raise ValueError(
                "Currently only PDF documents are supported."
            )

        documents = load_pdf(str(path))

        return documents

    # =========================================================
    # Split Document
    # =========================================================

    def split_document(
        self,
        documents: list[Document],
    ) -> list[Document]:
        """
        Split loaded documents into smaller chunks.
        """

        chunks = split_documents(documents)

        return chunks

    # =========================================================
    # Load + Split
    # =========================================================

    def process_document(
        self,
        file_path: str,
    ) -> list[Document]:
        """
        Complete Phase 4.1 + 4.2 pipeline:

        PDF
          ↓
        Load
          ↓
        Split
          ↓
        Chunks
        """

        documents = self.load_document(file_path)

        chunks = self.split_document(documents)

        return chunks