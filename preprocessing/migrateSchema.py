from shared_proxy import database

def main():

  db = database.connect_configured_database()
  db.update_schema()

if __name__ == "__main__":
  main()
