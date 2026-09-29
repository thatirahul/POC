# import os
# import json

# from flask import Flask, jsonify


# app = Flask(__name__)


# @app.get("/health")
# def health():
#     return jsonify({
#         "status": "UP",
#         "message": "SAP AI Agent HANA test application is running"
#     })


# @app.get("/debug/services")
# def debug_services():
#     vcap_services = os.getenv("VCAP_SERVICES")

#     if not vcap_services:
#         return jsonify({
#             "vcap_services": "NOT AVAILABLE"
#         }), 500

#     services = json.loads(vcap_services)

#     return jsonify({
#         "service_types": list(services.keys())
#     })


# if __name__ == "__main__":
#     port = int(os.getenv("PORT", "8080"))

#     app.run(
#         host="0.0.0.0",
#         port=port
#     )
import os
import json

from flask import Flask, jsonify
from hdbcli import dbapi


app = Flask(__name__)


# =========================================================
# Health Check
# =========================================================

@app.get("/health")
def health():
    return jsonify({
        "status": "UP",
        "message": "SAP AI Agent HANA test application is running"
    })


# =========================================================
# Debug VCAP_SERVICES
# =========================================================

@app.get("/debug/services")
def debug_services():

    vcap_services = os.getenv("VCAP_SERVICES")

    if not vcap_services:
        return jsonify({
            "status": "ERROR",
            "message": "VCAP_SERVICES is not available"
        }), 500

    try:
        services = json.loads(vcap_services)

        return jsonify({
            "status": "OK",
            "service_types": list(services.keys())
        })

    except json.JSONDecodeError as error:

        return jsonify({
            "status": "ERROR",
            "message": "Unable to parse VCAP_SERVICES",
            "error": str(error)
        }), 500


# =========================================================
# Get HANA Credentials
# =========================================================

def get_hana_credentials():

    vcap_services = os.getenv("VCAP_SERVICES")

    if not vcap_services:
        raise RuntimeError(
            "VCAP_SERVICES is not available"
        )

    services = json.loads(vcap_services)

    # Search all bound services
    for service_type, service_list in services.items():

        for service in service_list:

            credentials = service.get(
                "credentials",
                {}
            )

            if (
                credentials.get("host")
                and credentials.get("port")
                and credentials.get("user")
                and credentials.get("password")
            ):
                return credentials

    raise RuntimeError(
        "HANA credentials were not found in VCAP_SERVICES"
    )


# =========================================================
# Create HANA Connection
# =========================================================

def create_hana_connection():

    credentials = get_hana_credentials()

    connection = dbapi.connect(
        address=credentials["host"],
        port=int(credentials["port"]),
        user=credentials["user"],
        password=credentials["password"]
    )

    return connection


# =========================================================
# Test HANA Connection
# =========================================================

@app.get("/debug/hana")
def debug_hana():

    connection = None

    try:

        connection = create_hana_connection()

        cursor = connection.cursor()

        cursor.execute("""
            SELECT CURRENT_USER
            FROM DUMMY
        """)

        result = cursor.fetchone()

        return jsonify({
            "status": "OK",
            "message": "Successfully connected to SAP HANA Cloud",
            "current_user": result[0]
        })

    except Exception as error:

        return jsonify({
            "status": "ERROR",
            "message": "HANA connection failed",
            "error": str(error)
        }), 500

    finally:

        if connection:
            connection.close()


# =========================================================
# Test Available Embedding Models
# =========================================================

@app.get("/debug/models")
def debug_models():

    connection = None

    try:

        connection = create_hana_connection()

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                MODEL_NAME,
                MODEL_VERSION,
                DEFAULT_TOKEN_LIMIT,
                MAX_TOKEN_LIMIT,
                VECTOR_DIMENSION
            FROM NLP_VECTOR_EMBEDDING_MODELS
            ORDER BY MODEL_NAME
        """)

        rows = cursor.fetchall()

        models = []

        for row in rows:

            models.append({
                "model_name": row[0],
                "model_version": row[1],
                "default_token_limit": row[2],
                "max_token_limit": row[3],
                "vector_dimension": row[4]
            })

        return jsonify({
            "status": "OK",
            "message": "Successfully retrieved HANA embedding models",
            "models": models
        })

    except Exception as error:

        return jsonify({
            "status": "ERROR",
            "message": "Unable to query HANA embedding models",
            "error": str(error)
        }), 500

    finally:

        if connection:
            connection.close()


# =========================================================
# Test SAP_NEB.20240715 Embedding
# =========================================================

@app.get("/debug/embedding")
def debug_embedding():

    connection = None

    test_text = (
        "SAP HANA Cloud provides a vector engine "
        "for semantic search and RAG applications."
    )

    model_name = "SAP_NEB.20240715"

    try:

        # -------------------------------------------------
        # Connect to HANA
        # -------------------------------------------------

        connection = create_hana_connection()

        cursor = connection.cursor()

        # -------------------------------------------------
        # Generate embedding
        # -------------------------------------------------

        query = """
            SELECT VECTOR_EMBEDDING(
                ?,
                'DOCUMENT',
                ?
            )
            FROM DUMMY
        """

        cursor.execute(
            query,
            (
                test_text,
                model_name
            )
        )

        result = cursor.fetchone()

        if not result:

            return jsonify({
                "status": "ERROR",
                "message": "No embedding result returned",
                "model": model_name
            }), 500

        embedding = result[0]

        # -------------------------------------------------
        # Convert embedding to string
        # -------------------------------------------------

        embedding_string = str(embedding)

        # -------------------------------------------------
        # Try to determine dimension
        # -------------------------------------------------

        vector_dimension = None

        try:

            vector_values = json.loads(
                embedding_string
            )

            if isinstance(vector_values, list):
                vector_dimension = len(vector_values)

        except (json.JSONDecodeError, TypeError):

            vector_dimension = None

        # -------------------------------------------------
        # Return result
        # -------------------------------------------------

        return jsonify({
            "status": "OK",
            "message": "SAP HANA embedding model is working",
            "model": model_name,
            "text_type": "DOCUMENT",
            "vector_dimension": vector_dimension,
            "embedding_preview": embedding_string[:500]
        })

    except Exception as error:

        return jsonify({
            "status": "ERROR",
            "message": "SAP_NEB.20240715 embedding test failed",
            "model": model_name,
            "error": str(error)
        }), 500

    finally:

        if connection:
            connection.close()


# =========================================================
# Local Development
# =========================================================

if __name__ == "__main__":

    port = int(
        os.getenv("PORT", "8080")
    )

    app.run(
        host="0.0.0.0",
        port=port
    )