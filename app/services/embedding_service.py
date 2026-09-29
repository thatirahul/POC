# from typing import List
# import requests
# from langchain_core.embeddings import Embeddings
# from app.config import Config


# class AICoreEmbeddings(Embeddings):
#     """
#     LangChain Embeddings implementation for
#     SAP AI Core text-embedding-3-small.
#     """

#     def __init__(self):

#         Config.validate()

#         if not Config.AICORE_CLIENT_ID:
#             raise ValueError(
#                 "AICORE_CLIENT_ID is missing"
#             )

#         if not Config.AICORE_CLIENT_SECRET:
#             raise ValueError(
#                 "AICORE_CLIENT_SECRET is missing"
#             )

#         if not Config.AICORE_AUTH_URL:
#             raise ValueError(
#                 "AICORE_AUTH_URL is missing"
#             )

#         if not Config.AICORE_BASE_URL:
#             raise ValueError(
#                 "AICORE_BASE_URL is missing"
#             )

#         if not Config.AICORE_RESOURCE_GROUP:
#             raise ValueError(
#                 "AICORE_RESOURCE_GROUP is missing"
#             )

#         if not Config.AICORE_EMBEDDING_DEPLOYMENT_ID:
#             raise ValueError(
#                 "AICORE_EMBEDDING_DEPLOYMENT_ID is missing"
#             )

#         self.client_id = Config.AICORE_CLIENT_ID
#         self.client_secret = Config.AICORE_CLIENT_SECRET

#         self.auth_url = (
#             Config.AICORE_AUTH_URL.rstrip("/")
#         )

#         self.base_url = (
#             Config.AICORE_BASE_URL.rstrip("/")
#         )

#         self.resource_group = (
#             Config.AICORE_RESOURCE_GROUP
#         )

#         self.deployment_id = (
#             Config.AICORE_EMBEDDING_DEPLOYMENT_ID
#         )

#         self.model_name = (
#             Config.AICORE_EMBEDDING_MODEL
#         )

#     # =====================================================
#     # Get OAuth Access Token
#     # =====================================================

#     def get_access_token(self) -> str:

#         token_url = (
#             f"{self.auth_url}/oauth/token"
#         )

#         response = requests.post(
#             token_url,
#             data={
#                 "grant_type": "client_credentials"
#             },
#             auth=(
#                 self.client_id,
#                 self.client_secret,
#             ),
#             timeout=30,
#         )

#         response.raise_for_status()

#         return response.json()["access_token"]

#     # =====================================================
#     # Get Embedding Deployment URL
#     # =====================================================

#     def get_deployment_url(self) -> str:

#         token = self.get_access_token()

#         url = (
#             f"{self.base_url}"
#             f"/v2/lm/deployments/"
#             f"{self.deployment_id}"
#         )

#         headers = {
#             "Authorization": f"Bearer {token}",
#             "AI-Resource-Group": self.resource_group,
#             "Accept": "application/json",
#         }

#         response = requests.get(
#             url,
#             headers=headers,
#             timeout=30,
#         )

#         response.raise_for_status()

#         deployment = response.json()

#         deployment_url = deployment.get(
#             "deploymentUrl"
#         )

#         if not deployment_url:
#             raise ValueError(
#                 "Deployment URL was not returned "
#                 "by SAP AI Core."
#             )

#         return deployment_url.rstrip("/")

#     # =====================================================
#     # Generate Embedding
#     # =====================================================

#     def _embed(self, text: str) -> List[float]:

#         if not text or not text.strip():
#             raise ValueError(
#                 "Text cannot be empty."
#             )

#         token = self.get_access_token()

#         deployment_url = (
#             self.get_deployment_url()
#         )

#         url = (
#             f"{deployment_url}"
#             f"/embeddings"
#             f"?api-version=2023-05-15"
#         )

#         headers = {
#             "Authorization": f"Bearer {token}",
#             "AI-Resource-Group": self.resource_group,
#             "Content-Type": "application/json",
#             "Accept": "application/json",
#         }

#         payload = {
#             "input": text
#         }

#         response = requests.post(
#             url,
#             headers=headers,
#             json=payload,
#             timeout=120,
#         )

#         response.raise_for_status()

#         data = response.json()

#         embedding_data = data.get("data")

#         if not embedding_data:
#             raise ValueError(
#                 f"Embedding data missing in response: "
#                 f"{data}"
#             )

#         embedding = embedding_data[0].get(
#             "embedding"
#         )

#         if not embedding:
#             raise ValueError(
#                 f"Embedding vector missing in response: "
#                 f"{data}"
#             )

#         return embedding

#     # =====================================================
#     # LangChain: Embed Documents
#     # =====================================================

#     def embed_documents(
#         self,
#         texts: List[str],
#     ) -> List[List[float]]:

#         embeddings = []

#         for text in texts:

#             embedding = self._embed(text)

#             embeddings.append(embedding)

#         return embeddings

#     # =====================================================
#     # LangChain: Embed Query
#     # =====================================================

#     def embed_query(
#         self,
#         text: str,
#     ) -> List[float]:

#         return self._embed(text)

from typing import List
import struct

from app.config import Config
from app.services.hana_connection import get_hana_connection


class EmbeddingService:
    """
    Generates embeddings using SAP HANA's native
    VECTOR_EMBEDDING function.

    Model:
        SAP_NEB.20240715

    Dimension:
        768
    """

    MODEL_NAME = Config.EMBEDDING_MODEL
    DIMENSION = Config.EMBEDDING_DIMENSION

    def __init__(self):
        self.connection = None

    def _get_connection(self):
        if self.connection is None:
            self.connection = get_hana_connection()

        return self.connection

    def generate_embedding(
        self,
        text: str,
        text_type: str = "DOCUMENT",
    ) -> List[float]:

        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        text_type = text_type.upper()

        if text_type not in {"DOCUMENT", "QUERY"}:
            raise ValueError(
                "text_type must be either DOCUMENT or QUERY."
            )

        connection = self._get_connection()
        cursor = connection.cursor()

        sql = """
            SELECT VECTOR_EMBEDDING(
                ?,
                ?,
                ?
            )
            FROM DUMMY
        """

        try:
            cursor.execute(
                sql,
                (
                    text,
                    text_type,
                    self.MODEL_NAME,
                ),
            )

            row = cursor.fetchone()

        finally:
            cursor.close()

        if not row or row[0] is None:
            raise RuntimeError(
                "HANA did not return an embedding."
            )

        embedding = row[0]

        # --------------------------------------------------
        # HANA REAL_VECTOR returned by hdbcli as memoryview
        # --------------------------------------------------

        if isinstance(embedding, memoryview):

            raw_bytes = embedding.tobytes()

            # HANA REAL_VECTOR contains binary vector data.
            # Convert binary data to Python float values.
            #
            # First 4 bytes contain vector metadata/header.
            # Remaining bytes contain 768 float32 values.

            vector_bytes = raw_bytes[4:]

            expected_bytes = self.DIMENSION * 4

            if len(vector_bytes) != expected_bytes:
                raise RuntimeError(
                    f"Unexpected vector binary size: "
                    f"{len(vector_bytes)} bytes. "
                    f"Expected {expected_bytes} bytes."
                )

            embedding = list(
                struct.unpack(
                    f"<{self.DIMENSION}f",
                    vector_bytes,
                )
            )

        # --------------------------------------------------
        # String fallback
        # --------------------------------------------------

        elif isinstance(embedding, str):

            embedding = embedding.strip()

            if (
                embedding.startswith("[")
                and embedding.endswith("]")
            ):
                embedding = embedding[1:-1]

            embedding = [
                float(value.strip())
                for value in embedding.split(",")
                if value.strip()
            ]

        else:

            embedding = list(embedding)

        # --------------------------------------------------
        # Validate dimension
        # --------------------------------------------------

        if len(embedding) != self.DIMENSION:
            raise RuntimeError(
                f"Unexpected embedding dimension: "
                f"{len(embedding)}. "
                f"Expected {self.DIMENSION}."
            )

        return embedding

    def generate_document_embedding(
        self,
        text: str,
    ) -> List[float]:

        return self.generate_embedding(
            text=text,
            text_type="DOCUMENT",
        )

    def generate_query_embedding(
        self,
        text: str,
    ) -> List[float]:

        return self.generate_embedding(
            text=text,
            text_type="QUERY",
        )

    def close(self):

        if self.connection:
            self.connection.close()
            self.connection = None