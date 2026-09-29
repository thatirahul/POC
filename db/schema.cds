namespace ai.chatbot;

using { cuid, managed } from '@sap/cds/common';

entity Documents : cuid, managed {
    documentId : String(200);
    fileName   : String(255);
    mimeType   : String(100);
    status     : String(50);
}

entity ChatHistory : cuid, managed {
    document : Association to Documents;
    question : LargeString;
    answer   : LargeString;
}