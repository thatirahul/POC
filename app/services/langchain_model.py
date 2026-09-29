import json
from typing import Any

from pydantic import PrivateAttr

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool
from collections.abc import Callable, Sequence

from app.services.ai_core_service import AICoreService


class AICoreChatModel(BaseChatModel):
    """
    LangChain ChatModel implementation for SAP AI Core.

    This class allows LangChain agents to communicate with
    an LLM deployed on SAP AI Core.
    """

    _ai_core: AICoreService = PrivateAttr()
    _bound_tools: list[dict[str, Any]] = PrivateAttr(
        default_factory=list
    )

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self._ai_core = AICoreService()

    # =========================================================
    # LangChain model identification
    # =========================================================

    @property
    def _llm_type(self) -> str:
        return "sap-ai-core"

    # =========================================================
    # Bind tools
    # =========================================================

    def bind_tools(
    self,
    tools: Sequence[
        dict[str, Any]
        | type
        | Callable[..., Any]
        | BaseTool
    ],
    *,
    tool_choice: str | None = None,
    **kwargs: Any,
) -> Runnable:
        """
        Convert LangChain tools into OpenAI-compatible
        tool definitions and bind them to the model.
        """

        openai_tools = [
            convert_to_openai_tool(tool)
            for tool in tools
        ]

        return self.bind(
            tools=openai_tools,
            tool_choice=tool_choice,
            **kwargs,
        )

    # =========================================================
    # Generate response
    # =========================================================

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Convert LangChain messages into SAP AI Core format,
        call SAP AI Core, then convert the response back
        into a LangChain ChatResult.
        """

        # -----------------------------------------------------
        # 1. Convert LangChain messages to AI Core messages
        # -----------------------------------------------------

        ai_core_messages: list[dict[str, Any]] = []

        for message in messages:

            # ---------------------------------------------
            # System message
            # ---------------------------------------------

            if isinstance(message, SystemMessage):
                ai_core_messages.append(
                    {
                        "role": "system",
                        "content": message.content,
                    }
                )

            # ---------------------------------------------
            # Human/user message
            # ---------------------------------------------

            elif isinstance(message, HumanMessage):
                ai_core_messages.append(
                    {
                        "role": "user",
                        "content": message.content,
                    }
                )

            # ---------------------------------------------
            # AI/assistant message
            # ---------------------------------------------

            elif isinstance(message, AIMessage):

                ai_core_message: dict[str, Any] = {
                    "role": "assistant",
                    "content": message.content,
                }

                # AIMessage can contain tool calls
                if message.tool_calls:

                    ai_core_message["tool_calls"] = [
                        {
                            "id": tool_call["id"],
                            "type": "function",
                            "function": {
                                "name": tool_call["name"],
                                "arguments": json.dumps(
                                    tool_call["args"]
                                ),
                            },
                        }
                        for tool_call in message.tool_calls
                    ]

                ai_core_messages.append(ai_core_message)

            # ---------------------------------------------
            # Tool result message
            # ---------------------------------------------

            elif isinstance(message, ToolMessage):
                ai_core_messages.append(
                    {
                        "role": "tool",
                        "content": message.content,
                        "tool_call_id": message.tool_call_id,
                    }
                )

        # -----------------------------------------------------
        # 2. Get tools passed by LangChain
        # -----------------------------------------------------

        tools = kwargs.get("tools")

        # -----------------------------------------------------
        # 3. Call SAP AI Core
        # -----------------------------------------------------

        response = self._ai_core.generate_response(
            messages=ai_core_messages,
            tools=tools,
        )

        # -----------------------------------------------------
        # 4. Extract AI Core response
        # -----------------------------------------------------

        message_data = response["choices"][0]["message"]

        content = message_data.get(
            "content",
            "",
        )

        # -----------------------------------------------------
        # 5. Extract tool calls from AI Core response
        # -----------------------------------------------------

        tool_calls: list[dict[str, Any]] = []

        raw_tool_calls = message_data.get(
            "tool_calls",
            [],
        )

        for tool_call in raw_tool_calls:

            function = tool_call["function"]

            arguments = function.get(
                "arguments",
                {},
            )

            # AI Core may return arguments as a JSON string
            if isinstance(arguments, str):

                try:
                    arguments = json.loads(arguments)

                except json.JSONDecodeError:
                    arguments = {}

            tool_calls.append(
                {
                    "name": function["name"],
                    "args": arguments,
                    "id": tool_call["id"],
                    "type": "tool_call",
                }
            )

        # -----------------------------------------------------
        # 6. Create LangChain AIMessage
        # -----------------------------------------------------

        langchain_ai_message = AIMessage(
            content=content,
            tool_calls=tool_calls,
        )

        # -----------------------------------------------------
        # 7. Create ChatGeneration
        # -----------------------------------------------------

        generation = ChatGeneration(
            message=langchain_ai_message,
        )

        # -----------------------------------------------------
        # 8. Return ChatResult
        # -----------------------------------------------------

        return ChatResult(
            generations=[generation],
        )