from app.services.hana_connection import get_hana_connection


def main():
    print("=" * 70)
    print("HANA CONNECTION TEST")
    print("=" * 70)

    connection = None

    try:
        connection = get_hana_connection()

        print("\nHANA connection successful!")

        cursor = connection.cursor()

        cursor.execute("""
            SELECT CURRENT_USER, CURRENT_SCHEMA
            FROM DUMMY
        """)

        result = cursor.fetchone()

        print("Current user:", result[0])
        print("Current schema:", result[1])

        cursor.close()

    except Exception as e:
        print("\nHANA connection failed:")
        print(e)

    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    main()