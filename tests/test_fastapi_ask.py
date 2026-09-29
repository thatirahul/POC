import requests


BASE_URL = "http://127.0.0.1:8000"

DOCUMENT_ID = "sap_cap"

QUESTION = "What is SAP CAP?"


def main():

    print("=" * 60)
    print("FASTAPI DOCUMENT QUESTION TEST")
    print("=" * 60)

    print(f"\nDocument ID: {DOCUMENT_ID}")

    print(f"Question: {QUESTION}")

    url = (
        f"{BASE_URL}/documents/"
        f"{DOCUMENT_ID}/ask"
    )

    payload = {
        "question": QUESTION
    }

    print(f"\nURL: {url}")

    print("\nSending question...")

    response = requests.post(
        url,
        json=payload,
        timeout=180
    )

    print(
        f"\nHTTP Status: "
        f"{response.status_code}"
    )

    try:
        data = response.json()

        print("\nResponse:")
        print(data)

    except Exception:

        print("\nResponse:")
        print(response.text)

        raise

    response.raise_for_status()

    print("\n" + "=" * 60)
    print("QUESTION SUCCESSFUL")
    print("=" * 60)

    print(
        f"\nDocument ID: "
        f"{data['document_id']}"
    )

    print(
        f"Question: "
        f"{data['question']}"
    )

    print(
        f"\nAI Answer:\n"
        f"{data['answer']}"
    )


if __name__ == "__main__":
    main()