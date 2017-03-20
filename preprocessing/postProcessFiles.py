import pandas as pd

def normalise_subject_area(subject_area):
  return subject_area.lower().title().replace(' And ', ' and ')

def normalise_subject_areas(csv_path):
  df = (
    pd.read_csv(csv_path + "/manuscript-themes.csv")
    .rename(columns={'theme': 'subject-area'})
  )
  df['subject-area'] = df['subject-area'].apply(normalise_subject_area)

  normalised_csv_filename = csv_path + '/manuscript-subject-areas-normalised.csv'
  normalised_pickle_filename = csv_path + '/manuscript-subject-areas-normalised.pickle'

  print("writing to:", normalised_csv_filename)
  df.to_csv(normalised_csv_filename)

  print("writing to:", normalised_pickle_filename)
  df.to_pickle(normalised_pickle_filename)

def main():
  csv_path = "../../csv"
  normalise_subject_areas(csv_path)
  print("done")

if __name__ == "__main__":
  main()
