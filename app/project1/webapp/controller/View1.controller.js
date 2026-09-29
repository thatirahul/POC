sap.ui.define([
    "sap/ui/core/mvc/Controller",
    "sap/ui/model/json/JSONModel",
    "sap/m/MessageToast",
    "sap/m/MessageBox"
], function (
    Controller,
    JSONModel,
    MessageToast,
    MessageBox
) {
    "use strict";

    return Controller.extend("project1.controller.View1", {

        // ============================================================
        // INIT
        // ============================================================

        onInit: function () {

            var oViewModel = new JSONModel({
                documentId: "",
                fileName: "",
                mimeType: "",
                fileData: "",
                question: "",
                answer: "",
                busy: false,
                busyText: "",
                sidebarOpen: false,
                chatStarted: false,

                  // Voice recognition state
                  isListening: false,

                greeting: this._getGreeting()
            });

            this.getView().setModel(oViewModel, "view");


            var oHistoryModel = new JSONModel({
                value: []
            });

            this.getView().setModel(oHistoryModel, "history");


            var oConversationModel = new JSONModel({
                messages: []
            });

            this.getView().setModel(
                oConversationModel,
                "conversation"
            );


            this.onRefreshHistory();
        },


        // ============================================================
        // GREETING
        // ============================================================

        _getGreeting: function () {

            var iHour = new Date().getHours();

            if (iHour < 12) {
                return "Good Morning, Rahul";
            }

            if (iHour < 17) {
                return "Good Afternoon, Rahul";
            }

            return "Good Evening, Rahul";
        },


        // ============================================================
        // SIDEBAR
        // ============================================================

        onToggleSidebar: function () {

            var oModel = this.getView().getModel("view");

            var bOpen =
                oModel.getProperty("/sidebarOpen");

            oModel.setProperty(
                "/sidebarOpen",
                !bOpen
            );
        },


        // ============================================================
        // NEW CHAT
        // ============================================================

        onNewChat: function () {

            var oViewModel =
                this.getView().getModel("view");

            var oConversationModel =
                this.getView().getModel("conversation");


            oViewModel.setProperty("/question", "");
            oViewModel.setProperty("/answer", "");
            oViewModel.setProperty("/chatStarted", false);
            oViewModel.setProperty("/sidebarOpen", false);

            oConversationModel.setData({
                messages: []
            });
        },


        // ============================================================
        // OPEN FILE UPLOADER
        // ============================================================

        onOpenFileUploader: function () {

            var oUploader = this.byId("fileUploader");

            if (!oUploader) {
                MessageBox.error(
                    "File uploader is not available."
                );
                return;
            }

            /*
             * FileUploader wraps a native HTML input.
             * Trigger the file selection dialog.
             */

            var oDomRef = oUploader.getFocusDomRef();

            if (oDomRef) {
                oDomRef.click();
            }
        },


        // ============================================================
        // FILE CHANGE
        // ============================================================

        onFileChange: function (oEvent) {

            var aFiles =
                oEvent.getParameter("files");

            if (!aFiles || aFiles.length === 0) {
                return;
            }

            var oFile = aFiles[0];


            if (
                oFile.type !== "application/pdf" &&
                !oFile.name.toLowerCase().endsWith(".pdf")
            ) {

                MessageBox.error(
                    "Please select a PDF file."
                );

                return;
            }


            var oViewModel =
                this.getView().getModel("view");


            oViewModel.setProperty(
                "/fileName",
                oFile.name
            );

            oViewModel.setProperty(
                "/mimeType",
                oFile.type || "application/pdf"
            );

            oViewModel.setProperty(
                "/documentId",
                ""
            );


            var oReader = new FileReader();


            oReader.onload = async function (oLoadEvent) {

                try {

                    var sResult =
                        oLoadEvent.target.result;

                    var sBase64 =
                        sResult.split(",")[1];


                    oViewModel.setProperty(
                        "/fileData",
                        sBase64
                    );


                    MessageToast.show(
                        "PDF selected: " + oFile.name
                    );


                    /*
                     * Automatically upload the document
                     * after selecting it from the + button.
                     */

                    await this.onUploadDocument();

                } catch (oError) {

                    console.error(
                        "File processing error:",
                        oError
                    );

                    MessageBox.error(
                        "Unable to process the selected file."
                    );
                }

            }.bind(this);


            oReader.onerror = function () {

                MessageBox.error(
                    "Unable to read the selected file."
                );
            };


            oReader.readAsDataURL(oFile);
        },


        // ============================================================
        // UPLOAD DOCUMENT
        // ============================================================

        onUploadDocument: async function () {

            var oViewModel =
                this.getView().getModel("view");


            var sFileName =
                oViewModel.getProperty("/fileName");

            var sMimeType =
                oViewModel.getProperty("/mimeType");

            var sFileData =
                oViewModel.getProperty("/fileData");


            if (!sFileName || !sFileData) {

                MessageBox.warning(
                    "Please select a PDF document."
                );

                return;
            }


            oViewModel.setProperty("/busy", true);

            oViewModel.setProperty(
                "/busyText",
                "Processing document..."
            );


            try {

                var oPayload = {

                    fileName: sFileName,

                    mimeType:
                        sMimeType ||
                        "application/pdf",

                    fileData: sFileData
                };


                var oResponse = await fetch(
                    "/odata/v4/ai/UploadDocument",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(oPayload)
                    }
                );


                var oData =
                    await oResponse.json();


                if (!oResponse.ok) {

                    var sErrorMessage =
                        oData?.error?.message ||
                        oData?.message ||
                        "Document upload failed.";

                    throw new Error(
                        sErrorMessage
                    );
                }


                oViewModel.setProperty(
                    "/documentId",
                    oData.documentId
                );


                var oUploadMessage =
                    this.byId("uploadMessage");


                if (oUploadMessage) {

                    oUploadMessage.setText(
                        "Document ready: " +
                        (oData.filename || sFileName)
                    );

                    oUploadMessage.setType(
                        "Success"
                    );

                    oUploadMessage.setVisible(
                        true
                    );
                }


                MessageToast.show(
                    "Document processed successfully."
                );

            } catch (oError) {

                console.error(
                    "Upload error:",
                    oError
                );


                MessageBox.error(
                    oError.message ||
                    "Unable to upload document."
                );

            } finally {

                oViewModel.setProperty(
                    "/busy",
                    false
                );

                oViewModel.setProperty(
                    "/busyText",
                    ""
                );
            }
        },


        // ============================================================
        // ASK QUESTION
        // ============================================================

        onAskQuestion: async function () {

            var oViewModel =
                this.getView().getModel("view");

            var oConversationModel =
                this.getView().getModel(
                    "conversation"
                );


            var sDocumentId =
                oViewModel.getProperty(
                    "/documentId"
                );

            var sQuestion =
                oViewModel.getProperty(
                    "/question"
                );


            if (!sDocumentId) {

                MessageBox.warning(
                    "Please upload a PDF document using the + button first."
                );

                return;
            }


            if (!sQuestion || !sQuestion.trim()) {

                MessageBox.warning(
                    "Please enter a question."
                );

                return;
            }


            sQuestion = sQuestion.trim();


            // Add user message to conversation

            var aMessages =
                oConversationModel.getProperty(
                    "/messages"
                ) || [];


            aMessages.push({
                role: "user",
                text: this._escapeHtml(sQuestion)
            });


            oConversationModel.setProperty(
                "/messages",
                aMessages
            );


            oViewModel.setProperty(
                "/chatStarted",
                true
            );


            // Clear input

            oViewModel.setProperty(
                "/question",
                ""
            );


            oViewModel.setProperty(
                "/busy",
                true
            );

            oViewModel.setProperty(
                "/busyText",
                "Thinking..."
            );


            try {

                var oPayload = {

                    documentId:
                        sDocumentId,

                    question:
                        sQuestion
                };


                var oResponse = await fetch(
                    "/odata/v4/ai/AskQuestion",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(oPayload)
                    }
                );


                var oData =
                    await oResponse.json();


                if (!oResponse.ok) {

                    var sErrorMessage =
                        oData?.error?.message ||
                        oData?.message ||
                        "Unable to get AI response.";

                    throw new Error(
                        sErrorMessage
                    );
                }


                oViewModel.setProperty(
                    "/answer",
                    oData.answer
                );


                aMessages =
                    oConversationModel.getProperty(
                        "/messages"
                    ) || [];


                aMessages.push({
                    role: "assistant",
                    text: oData.answer
                });


                oConversationModel.setProperty(
                    "/messages",
                    aMessages
                );


                await this.onRefreshHistory();


                setTimeout(function () {
                    this._scrollToBottom();
                }.bind(this), 150);


            } catch (oError) {

                console.error(
                    "AskQuestion error:",
                    oError
                );


                MessageBox.error(
                    oError.message ||
                    "Unable to process the question."
                );

            } finally {

                oViewModel.setProperty(
                    "/busy",
                    false
                );

                oViewModel.setProperty(
                    "/busyText",
                    ""
                );
            }
        },


        // ============================================================
       // VOICE INPUT - START / STOP 
      // ============================================================

onVoiceInput: function () {

    var oViewModel =
        this.getView().getModel("view");

    var SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;


    // --------------------------------------------------------
    // Browser support
    // --------------------------------------------------------

    if (!SpeechRecognition) {

        MessageBox.information(
            "Voice input is not supported by this browser. Please use Chrome or Edge."
        );

        return;
    }


    // --------------------------------------------------------
    // If already listening -> STOP
    // --------------------------------------------------------

    if (oViewModel.getProperty("/isListening")) {

        if (this._oRecognition) {
            this._oRecognition.stop();
        }

        oViewModel.setProperty(
            "/isListening",
            false
        );

        return;
    }


    // --------------------------------------------------------
    // Create recognition instance
    // --------------------------------------------------------

    if (!this._oRecognition) {

        this._oRecognition =
            new SpeechRecognition();


        this._oRecognition.lang =
            "en-IN";


        this._oRecognition.interimResults =
            true;


        this._oRecognition.continuous =
            true;


        this._oRecognition.maxAlternatives =
            1;


        // ----------------------------------------------------
        // Speech result
        // ----------------------------------------------------

        this._oRecognition.onresult =
            function (oEvent) {

                var sFinalText = "";
                var sInterimText = "";


                for (
                    var i = oEvent.resultIndex;
                    i < oEvent.results.length;
                    i++
                ) {

                    var sTranscript =
                        oEvent.results[i][0]
                            .transcript;


                    if (oEvent.results[i].isFinal) {

                        sFinalText +=
                            sTranscript;

                    } else {

                        sInterimText +=
                            sTranscript;
                    }
                }


                var sText =
                    sFinalText ||
                    sInterimText;


                if (sText) {

                    oViewModel.setProperty(
                        "/question",
                        sText.trim()
                    );
                }

            }.bind(this);


        // ----------------------------------------------------
        // Recognition finished
        // ----------------------------------------------------

        this._oRecognition.onend =
            function () {

                oViewModel.setProperty(
                    "/isListening",
                    false
                );

            }.bind(this);


        // ----------------------------------------------------
        // Recognition error
        // ----------------------------------------------------

        this._oRecognition.onerror =
            function (oEvent) {

                console.error(
                    "Speech recognition error:",
                    oEvent.error
                );


                oViewModel.setProperty(
                    "/isListening",
                    false
                );


                if (
                    oEvent.error !== "no-speech" &&
                    oEvent.error !== "aborted"
                ) {

                    MessageToast.show(
                        "Unable to recognize voice."
                    );
                }

            }.bind(this);
    }


    // --------------------------------------------------------
    // START LISTENING
    // --------------------------------------------------------

    try {

        oViewModel.setProperty(
            "/isListening",
            true
        );


        this._oRecognition.start();


        MessageToast.show(
            "Listening..."
        );

    } catch (oError) {

        console.error(
            "Microphone error:",
            oError
        );


        oViewModel.setProperty(
            "/isListening",
            false
        );
    }
},
onNewChat: function () {

    var oViewModel =
        this.getView().getModel("view");

    var oConversationModel =
        this.getView().getModel("conversation");


    // Stop voice recognition if active

    if (this._oRecognition) {

        try {
            this._oRecognition.stop();
        } catch (oError) {
            console.warn(
                "Unable to stop speech recognition:",
                oError
            );
        }
    }

    oViewModel.setProperty(
        "/isListening",
        false
    );


    oViewModel.setProperty("/question", "");
    oViewModel.setProperty("/answer", "");
    oViewModel.setProperty("/chatStarted", false);
    oViewModel.setProperty("/sidebarOpen", false);

    oConversationModel.setData({
        messages: []
    });
},
        // ============================================================
        // REFRESH CHAT HISTORY
        // ============================================================

        onRefreshHistory: async function () {

            var oHistoryModel =
                this.getView().getModel(
                    "history"
                );


            try {

                var oResponse = await fetch(
                    "/odata/v4/ai/ChatHistory?$orderby=createdAt desc",
                    {
                        method: "GET",

                        headers: {
                            "Accept":
                                "application/json"
                        }
                    }
                );


                var oData =
                    await oResponse.json();


                if (!oResponse.ok) {

                    throw new Error(
                        oData?.error?.message ||
                        "Unable to load chat history."
                    );
                }


                oHistoryModel.setData({
                    value:
                        oData.value || []
                });


            } catch (oError) {

                console.error(
                    "Chat history error:",
                    oError
                );
            }
        },


        // ============================================================
        // SCROLL CHAT TO BOTTOM
        // ============================================================

        _scrollToBottom: function () {

            var oScroll =
                this.byId(
                    "conversationScroll"
                );


            if (!oScroll) {
                return;
            }


            var oDomRef =
                oScroll.getDomRef();


            if (oDomRef) {

                oDomRef.scrollTop =
                    oDomRef.scrollHeight;
            }
        },


        // ============================================================
        // ESCAPE USER TEXT
        // ============================================================

        _escapeHtml: function (sText) {

            return String(sText)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        },
    // ============================================================
// OPEN CHAT FROM HISTORY
// ============================================================

onHistoryItemPress: function (oEvent) {

    var oContext =
        oEvent.getSource().getBindingContext("history");

    if (!oContext) {
        return;
    }

    var oHistoryItem =
        oContext.getObject();

    if (!oHistoryItem) {
        return;
    }


    var sQuestion =
        oHistoryItem.question || "";

    var sAnswer =
        oHistoryItem.answer || "";


    var oViewModel =
        this.getView().getModel("view");

    var oConversationModel =
        this.getView().getModel("conversation");


    // Clear current question input
    oViewModel.setProperty(
        "/question",
        ""
    );


    // Open conversation screen
    oViewModel.setProperty(
        "/chatStarted",
        true
    );


    // Optional:
    // close sidebar after selecting history
    oViewModel.setProperty(
        "/sidebarOpen",
        false
    );


    // Show selected history conversation
    oConversationModel.setData({
        messages: [
            {
                role: "user",
                text: this._escapeHtml(sQuestion)
            },
            {
                role: "assistant",
                text: sAnswer
            }
        ]
    });


    // Scroll conversation to top
    setTimeout(function () {

        var oScroll =
            this.byId("conversationScroll");

        if (!oScroll) {
            return;
        }


        var oDomRef =
            oScroll.getDomRef();

        if (oDomRef) {
            oDomRef.scrollTop = 0;
        }

    }.bind(this), 100);
},

    });
});