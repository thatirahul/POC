using { ai.chatbot as db } from '../db/schema';

service AIService {

    entity Documents as projection on db.Documents;
    entity ChatHistory as projection on db.ChatHistory;

    type UploadResult {
        message    : String;
        documentId : String;
        filename   : String;
        pages      : Integer;
        chunks     : Integer;
    }

    type AskResult {
        documentId : String;
        question   : String;
        answer     : LargeString;
    }

    action UploadDocument(
        fileName : String,
        mimeType : String,
        fileData : LargeString
    ) returns UploadResult;

    action AskQuestion(
        documentId : String,
        question   : String
    ) returns AskResult;
}