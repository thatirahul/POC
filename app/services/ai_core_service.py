
import requests

from app.config import Config


class AICoreService:

    def __init__(self):

        # Validate all required configuration values
        Config.validate()

        # After validation, these values are expected to be strings
        if not Config.AICORE_CLIENT_ID:
            raise ValueError("AICORE_CLIENT_ID is missing")

        if not Config.AICORE_CLIENT_SECRET:
            raise ValueError("AICORE_CLIENT_SECRET is missing")

        if not Config.AICORE_AUTH_URL:
            raise ValueError("AICORE_AUTH_URL is missing")

        if not Config.AICORE_BASE_URL:
            raise ValueError("AICORE_BASE_URL is missing")

        if not Config.AICORE_RESOURCE_GROUP:
            raise ValueError("AICORE_RESOURCE_GROUP is missing")

        if not Config.AICORE_DEPLOYMENT_ID:
            raise ValueError("AICORE_DEPLOYMENT_ID is missing")

        self.client_id = Config.AICORE_CLIENT_ID
        self.client_secret = Config.AICORE_CLIENT_SECRET
        self.auth_url = Config.AICORE_AUTH_URL.rstrip("/")
        self.base_url = Config.AICORE_BASE_URL.rstrip("/")
        self.resource_group = Config.AICORE_RESOURCE_GROUP
        self.deployment_id = Config.AICORE_DEPLOYMENT_ID
    # -----------------------------------------------------
    # Get OAuth Access Token
    # -----------------------------------------------------

    def get_access_token(self):

        token_url = (
            f"{self.auth_url}/oauth/token"
        )

        response = requests.post(
            token_url,
            data={
                "grant_type": "client_credentials"
            },
            auth=(
                self.client_id,
                self.client_secret
            ),
            timeout=30
        )

        response.raise_for_status()

        return response.json()["access_token"]

    # -----------------------------------------------------
    # Get Deployment Information
    # -----------------------------------------------------

    def get_deployment(self):

        token = self.get_access_token()

        url = (
            f"{self.base_url}"
            f"/v2/lm/deployments/"
            f"{self.deployment_id}"
        )

        headers = {
            "Authorization": f"Bearer {token}",
            "AI-Resource-Group": self.resource_group,
            "Accept": "application/json"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        return response.json()

        # -----------------------------------------------------
    # Send Chat Completion Request
    # -----------------------------------------------------

    def generate_response(self, messages, tools=None):

        token = self.get_access_token()

        deployment = self.get_deployment()

        deployment_url = (
            deployment["deploymentUrl"]
            .rstrip("/")
        )

        url = (
            f"{deployment_url}"
            f"/chat/completions"
            f"?api-version=2023-05-15"
        )

        headers = {
            "Authorization": f"Bearer {token}",
            "AI-Resource-Group": self.resource_group,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload = {
            "messages": messages,
            "max_completion_tokens": 2000
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=120
        )

        if not response.ok:
            print("\n" + "=" * 60)
            print("SAP AI CORE ERROR")
            print("=" * 60)
            print(f"HTTP Status: {response.status_code}")
            print(f"Response: {response.text}")
            print("=" * 60)

        response.raise_for_status()

        result = response.json()

        print("\n========== SAP AI CORE RAW RESPONSE ==========")
        print(result)

        # Return only the AI-generated answer
        return result["choices"][0]["message"]["content"]