from app.agent.agent import create_chat_agent


def main():

    print("Starting Phase 3 application...")

    agent = create_chat_agent()

    question = input(
        "\nAsk your question: "
    )

    response = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": question
            }
        ]
    })

    print("\n========== DEBUG RESPONSE ==========")
    print(repr(response))

    print("\n========== MESSAGES ==========")

    for i, message in enumerate(response["messages"]):
        print(f"\nMessage {i}")
        print("Type:", type(message))
        print("Content:", repr(message.content))
        print("Additional kwargs:", message.additional_kwargs)

    final_message = response["messages"][-1]

    print("\n========== AI RESPONSE ==========")
    print(repr(final_message.content))


if __name__ == "__main__":
    main()