import json
import os

from hdbcli import dbapi

from app.config import Config


def get_hana_connection():
    """
    Create a connection to SAP HANA Cloud.

    Supports:
    1. Cloud Foundry using VCAP_SERVICES
    2. Local development using .env
    """

    # ==================================================
    # CLOUD FOUNDRY
    # ==================================================

    vcap_services = os.getenv("VCAP_SERVICES")

    if vcap_services:

        services = json.loads(vcap_services)

        hana_services = services.get(
            "hana",
            []
        )

        if not hana_services:
            raise RuntimeError(
                "No HANA service found "
                "in VCAP_SERVICES."
            )

        credentials = (
            hana_services[0]["credentials"]
        )

        host = credentials["host"]
        port = int(
            credentials.get(
                "port",
                443
            )
        )

        user = credentials["user"]
        password = credentials["password"]

        # IMPORTANT:
        # This is the actual HDI container schema
        schema = credentials.get("schema")

        connection = dbapi.connect(
            address=host,
            port=port,
            user=user,
            password=password,
            encrypt=True,
        )

        # ----------------------------------------------
        # Set HDI container schema
        # ----------------------------------------------

        if schema:

            cursor = connection.cursor()

            try:

                cursor.execute(
                    f'SET SCHEMA "{schema}"'
                )

            finally:

                cursor.close()

        return connection

    # ==================================================
    # LOCAL DEVELOPMENT
    # ==================================================

    required = [
        Config.HANA_HOST,
        Config.HANA_USER,
        Config.HANA_PASSWORD,
    ]

    if not all(required):

        raise RuntimeError(
            "HANA configuration is missing. "
            "Set HANA_HOST, HANA_USER "
            "and HANA_PASSWORD."
        )

    connection = dbapi.connect(
        address=Config.HANA_HOST,
        port=Config.HANA_PORT,
        user=Config.HANA_USER,
        password=Config.HANA_PASSWORD,
        encrypt=True,
    )

    # ----------------------------------------------
    # Set configured schema locally
    # ----------------------------------------------

    schema = Config.HANA_SCHEMA

    if schema:

        cursor = connection.cursor()

        try:

            cursor.execute(
                f'SET SCHEMA "{schema}"'
            )

        finally:

            cursor.close()

    return connection