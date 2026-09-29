import cds from "@sap/cds";
import dotenv from "dotenv";

dotenv.config();

const PYTHON_BASE_URL = process.env.PYTHON_API_BASE_URL;

if (!PYTHON_BASE_URL) {
    throw new Error(
        "PYTHON_API_BASE_URL is not configured in environment variables."
    );
}

export default cds.service.impl(function () {

    const { Documents, ChatHistory } = this.entities;

    // ============================================================
    // UPLOAD DOCUMENT
    // ============================================================

    this.on("UploadDocument", async (req) => {

        const {
            fileName,
            mimeType,
            fileData
        } = req.data;

        if (!fileName || !fileName.trim()) {
            return req.reject(
                400,
                "File name is required."
            );
        }

        if (!fileData || !fileData.trim()) {
            return req.reject(
                400,
                "File data is required."
            );
        }

        try {

            const base64Data = fileData.includes(",")
                ? fileData.split(",")[1]
                : fileData;

            const fileBuffer = Buffer.from(
                base64Data,
                "base64"
            );

            const formData = new FormData();

            const blob = new Blob(
                [fileBuffer],
                {
                    type: mimeType || "application/pdf"
                }
            );

            formData.append(
                "file",
                blob,
                fileName
            );

            console.log(
                `Uploading document to Python API: ${fileName}`
            );

            const response = await fetch(
                `${PYTHON_BASE_URL}/documents/upload`,
                {
                    method: "POST",
                    body: formData
                }
            );

            const rawResponse = await response.text();

            console.log(
                "Python upload status:",
                response.status
            );

            console.log(
                "Python upload raw response:",
                rawResponse
            );

            let data;

            try {
                data = JSON.parse(rawResponse);
            } catch {
                return req.reject(
                    502,
                    `Python upload service returned invalid JSON. HTTP status: ${response.status}`
                );
            }

            if (!response.ok) {
                return req.reject(
                    response.status,
                    data.detail ||
                    data.message ||
                    "Python document upload failed."
                );
            }

            // ----------------------------------------------------
            // Save metadata in CAP database
            // ----------------------------------------------------

            const tx = cds.tx(req);

            const existingDocument =
                await tx.run(
                    SELECT.one
                        .from(Documents)
                        .where({
                            documentId: data.document_id
                        })
                );

            if (existingDocument) {

                await tx.run(
                    UPDATE(Documents)
                        .set({
                            fileName: data.filename,
                            mimeType:
                                mimeType ||
                                "application/pdf",
                            status: "PROCESSED"
                        })
                        .where({
                            ID: existingDocument.ID
                        })
                );

            } else {

                await tx.run(
                    INSERT.into(Documents)
                        .entries({
                            documentId:
                                data.document_id,
                            fileName:
                                data.filename,
                            mimeType:
                                mimeType ||
                                "application/pdf",
                            status:
                                "PROCESSED"
                        })
                );
            }

            console.log(
                "Document metadata stored in CAP database."
            );

            return {
                message: data.message,
                documentId: data.document_id,
                filename: data.filename,
                pages: data.pages,
                chunks: data.chunks
            };

        } catch (error) {

            console.error(
                "UploadDocument error:",
                error
            );

            return req.reject(
                500,
                `Unable to upload document: ${error.message}`
            );
        }
    });


    // ============================================================
    // ASK QUESTION
    // ============================================================

    this.on("AskQuestion", async (req) => {

        const {
            documentId,
            question
        } = req.data;

        if (!documentId || !documentId.trim()) {
            return req.reject(
                400,
                "Document ID is required."
            );
        }

        if (!question || !question.trim()) {
            return req.reject(
                400,
                "Question is required."
            );
        }

        try {

            const url =
                `${PYTHON_BASE_URL}/documents/${encodeURIComponent(documentId)}/ask`;

            console.log(
                "Calling Python RAG API:"
            );

            console.log(url);

            const response = await fetch(
                url,
                {
                    method: "POST",
                    headers: {
                        "Content-Type":
                            "application/json"
                    },
                    body: JSON.stringify({
                        question
                    })
                }
            );

            const rawResponse =
                await response.text();

            console.log(
                "Python response status:",
                response.status
            );

            console.log(
                "Python raw response:",
                rawResponse
            );

            let data;

            try {
                data = JSON.parse(rawResponse);
            } catch {
                return req.reject(
                    502,
                    `Python service returned invalid JSON. HTTP status: ${response.status}`
                );
            }

            if (!response.ok) {
                return req.reject(
                    response.status,
                    data.detail ||
                    data.message ||
                    "Python RAG API request failed."
                );
            }

            // ----------------------------------------------------
            // Find corresponding CAP document
            // ----------------------------------------------------

            const tx = cds.tx(req);

            const document =
                await tx.run(
                    SELECT.one
                        .from(Documents)
                        .where({
                            documentId
                        })
                );

            // ----------------------------------------------------
            // Store chat history
            // ----------------------------------------------------

            if (document) {

                await tx.run(
                    INSERT.into(ChatHistory)
                        .entries({
                            document_ID:
                                document.ID,
                            question:
                                data.question,
                            answer:
                                data.answer
                        })
                );

                console.log(
                    "Chat history stored in CAP database."
                );

            } else {

                console.warn(
                    `Document '${documentId}' exists in Python/HANA but is not registered in CAP Documents.`
                );
            }

            console.log(
                "Python RAG response received successfully."
            );

            return {
                documentId:
                    data.document_id,
                question:
                    data.question,
                answer:
                    data.answer
            };

        } catch (error) {

            console.error(
                "AskQuestion error:",
                error
            );

            return req.reject(
                500,
                `Unable to call Python RAG service: ${error.message}`
            );
        }
    });

});