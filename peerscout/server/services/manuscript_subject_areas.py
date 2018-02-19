from peerscout.utils.collection import (
  iter_flatten,
  groupby_to_dict,
  applymap_dict
)

class ManuscriptSubjectAreaService:
  def __init__(self, df):
    self._df = df
    self._subject_areas_by_id_map = df.groupby('version_id')['subject_area'].apply(sorted).to_dict()

  @staticmethod
  def from_database(db, valid_version_ids=None):
    df = db.manuscript_subject_area.read_frame()
    if valid_version_ids is not None:
      df = df[df['version_id'].isin(valid_version_ids)]
    return ManuscriptSubjectAreaService(df)

  def get_ids_by_subject_areas(self, subject_areas):
    df = self._df[self._df['subject_area'].str.lower().isin(
      [s.lower() for s in subject_areas]
    )]
    return set(df['version_id'])

  def get_subject_areas_by_id(self, manuscript_version_id):
    return self._subject_areas_by_id_map.get(manuscript_version_id, [])

  def get_all_subject_areas(self):
    return set(self._df['subject_area'].unique())
