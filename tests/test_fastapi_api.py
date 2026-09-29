from pathlib import Path

import requests


BASE_URL = "http://127.0.0.1:8000"


def main():

    print("=" * 60)
    print("FASTAPI DOCUMENT UPLOAD TEST")
    print("=" * 60)

    pdf_path = Path("documents/sap_cap.pdf")

    if not pdf_path.exists():
        print(f"\nERROR: File not found: {pdf_path}")
        return

    url = f"{BASE_URL}/documents/upload"

    print("\nUploading file...")
    print(f"File: {pdf_path}")
    print(f"URL: {url}")

    try:

        with pdf_path.open("rb") as file:

            files = {
                "file": (
                    pdf_path.name,
                    file,
                    "application/pdf",
                )
            }

            response = requests.post(
                url,
                files=files,
                timeout=300,
            )

        print(f"\nHTTP Status: {response.status_code}")

        print("\nResponse:")

        try:
            print(response.json())
        except ValueError:
            print(response.text)

        response.raise_for_status()

        data = response.json()

        print("\n" + "=" * 60)
        print("UPLOAD SUCCESSFUL")
        print("=" * 60)

        print(
            f"Document ID: "
            f"{data['document_id']}"
        )

        print(
            f"Filename: "
            f"{data['filename']}"
        )

        print(
            f"Pages: "
            f"{data['pages']}"
        )

        print(
            f"Chunks: "
            f"{data['chunks']}"
        )

    except requests.exceptions.RequestException as e:

        print("\nAPI REQUEST FAILED")
        print(e)


if __name__ == "__main__":
    main()