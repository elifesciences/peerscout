from shared_proxy import database

def main():

  with database.connect_managed_configured_database() as db:
    db.update_schema()

if __name__ == "__main__":
  main()
