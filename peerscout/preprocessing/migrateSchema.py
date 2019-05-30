from ..shared.database import connect_managed_configured_database


def main():

    with connect_managed_configured_database() as db:
        db.update_schema()


if __name__ == "__main__":
    main()
