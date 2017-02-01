import pandas as pd

def main():
  csv_path = "../csv"

  persons_df = pd.read_csv(csv_path + "/persons.csv")

  # persons_df['profile-modify-date'] = persons_df['profile-modify-date'].apply(pd.to_datetime)

  last_person_df = persons_df.sort_values(by='profile-modify-date').groupby('person-id').last()

  last_person_df.to_csv(csv_path + '/persons-current.csv')

  print("done")

if __name__ == "__main__":
  main()
