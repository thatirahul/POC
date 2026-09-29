from pathlib import Path
import re
import shutil

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.rag.loader import load_pdf
from app.rag.splitter import split_documents
from app.services.embedding_service import EmbeddingService
from app.services.hana_vector_service import HanaVectorService
from app.services.rag_service import RAGService


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class AskRequest(BaseModel):
    question: str


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    # --------------------------------------------------
    # Validate file
    # --------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="File name is missing."
        )

    original_filename = Path(file.filename).name

    if not original_filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    # --------------------------------------------------
    # Create safe document ID
    # --------------------------------------------------

    document_id = Path(original_filename).stem

    document_id = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        document_id
    ).strip("_")

    if not document_id:
        raise HTTPException(
            status_code=400,
            detail="Invalid document name."
        )

    file_path = UPLOAD_DIR / original_filename

    try:

        # --------------------------------------------------
        # Save uploaded file
        # --------------------------------------------------

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        print(
            f"\nUploaded document: {original_filename}"
        )

        # --------------------------------------------------
        # Load PDF
        # --------------------------------------------------

        print("\nLoading PDF...")

        documents = load_pdf(
            str(file_path)
        )

        print(
            f"Pages loaded: {len(documents)}"
        )

        # --------------------------------------------------
        # Split document
        # --------------------------------------------------

        print("\nSplitting document...")

        chunks = split_documents(
            documents
        )

        print(
            f"Total chunks: {len(chunks)}"
        )

        # --------------------------------------------------
        # HANA services
        # --------------------------------------------------

        embedding_service = EmbeddingService()
        vector_service = HanaVectorService()

        try:

            # ----------------------------------------------
            # Replace existing document if re-uploaded
            # ----------------------------------------------

            vector_service.delete_document(
                document_id
            )

            # ----------------------------------------------
            # Generate embeddings and store chunks
            # ----------------------------------------------

            stored_chunks = 0

            for index, chunk in enumerate(chunks):

                chunk_text = (
                    chunk.page_content
                    .strip()
                )

                if not chunk_text:
                    continue

                chunk_id = (
                    f"{document_id}-chunk-{index}"
                )

                print(
                    f"\nProcessing chunk "
                    f"{index + 1}/{len(chunks)}..."
                )

                # SAP HANA Native Embedding
                # SAP_NEB.20240715
                # 768 dimensions

                embedding = (
                    embedding_service
                    .generate_document_embedding(
                        chunk_text
                    )
                )

                vector_service.insert_chunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    chunk_index=index,
                    chunk_text=chunk_text,
                    embedding=embedding,
                )

                stored_chunks += 1

                print(
                    "Stored successfully."
                )

        finally:

            embedding_service.close()
            vector_service.close()

        return {
            "message": (
                "Document uploaded and "
                "processed successfully."
            ),
            "document_id": document_id,
            "filename": original_filename,
            "pages": len(documents),
            "chunks": stored_chunks,
        }

    except HTTPException:
        raise

    except Exception as e:

        print(
            f"\nDocument processing error: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/{document_id}/ask")
async def ask_question(
    document_id: str,
    request: AskRequest
):

    # --------------------------------------------------
    # Validate question
    # --------------------------------------------------

    if not request.question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    # --------------------------------------------------
    # Check document exists
    # --------------------------------------------------

    vector_service = HanaVectorService()

    try:

        exists = vector_service.document_exists(
            document_id
        )

    finally:

        vector_service.close()

    if not exists:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Document '{document_id}' "
                "was not found."
            )
        )

    # --------------------------------------------------
    # RAG
    # --------------------------------------------------

    rag_service = RAGService()

    try:

        print(
            f"\nQuestion for document: "
            f"{document_id}"
        )

        print(
            f"Question: {request.question}"
        )

        answer = (
            rag_service
            .generate_answer(
                question=request.question,
                document_id=document_id,
                top_k=5,
            )
        )

        return {
            "document_id": document_id,
            "question": request.question,
            "answer": answer,
        }

    except Exception as e:

        print(
            f"\nRAG error: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        rag_service.close()