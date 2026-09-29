import os

from dotenv import load_dotenv

load_dotenv()


class Config:

    AICORE_CLIENT_ID = os.getenv("AICORE_CLIENT_ID")
    AICORE_CLIENT_SECRET = os.getenv("AICORE_CLIENT_SECRET")
    AICORE_AUTH_URL = os.getenv("AICORE_AUTH_URL")
    AICORE_BASE_URL = os.getenv("AICORE_BASE_URL")
    AICORE_RESOURCE_GROUP = os.getenv("AICORE_RESOURCE_GROUP")
    AICORE_DEPLOYMENT_ID = os.getenv("AICORE_DEPLOYMENT_ID")
                        # GPT deployment
    AICORE_DEPLOYMENT_ID = os.getenv(
        "AICORE_DEPLOYMENT_ID"
    )

    ## ------------------------------------------------------------------
    # HANA
    # ------------------------------------------------------------------

    HANA_HOST = os.getenv("HANA_HOST")
    HANA_PORT = int(os.getenv("HANA_PORT", "443"))
    HANA_USER = os.getenv("HANA_USER")
    HANA_PASSWORD = os.getenv("HANA_PASSWORD")
    HANA_SCHEMA = os.getenv("HANA_SCHEMA")

    # ------------------------------------------------------------------
    # HANA Native Embedding Model
    # ------------------------------------------------------------------

    EMBEDDING_MODEL = "SAP_NEB.20240715"
    EMBEDDING_DIMENSION = 768

    # ------------------------------------------------------------------
    # RAG
    # ------------------------------------------------------------------

    TOP_K = int(os.getenv("RAG_TOP_K", "5"))
    
    @classmethod
    def validate(cls):

        required = {
            "AICORE_CLIENT_ID": cls.AICORE_CLIENT_ID,
            "AICORE_CLIENT_SECRET": cls.AICORE_CLIENT_SECRET,
            "AICORE_AUTH_URL": cls.AICORE_AUTH_URL,
            "AICORE_BASE_URL": cls.AICORE_BASE_URL,
            "AICORE_RESOURCE_GROUP": cls.AICORE_RESOURCE_GROUP,
            "AICORE_DEPLOYMENT_ID": cls.AICORE_DEPLOYMENT_ID,
        }

        missing = [
            key for key, value in required.items()
            if not value
        ]

        if missing:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing)}"
            )