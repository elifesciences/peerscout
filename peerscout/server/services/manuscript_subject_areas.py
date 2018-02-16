from peerscout.utils.collection import (
  iter_flatten,
  groupby_to_dict,
  applymap_dict
)

class ManuscriptSubjectAreaService:
  def __init__(self, ids_by_subject_area_map, subject_areas_by_id_map, all_subject_areas):
    self._ids_by_subject_area_map = ids_by_subject_area_map
    self._subject_areas_by_id_map = subject_areas_by_id_map
    self._all_subject_areas = all_subject_areas

  @staticmethod
  def from_database(db, valid_version_ids=None):
    query = db.session.query(
      db.manuscript_subject_area.table.version_id,
      db.manuscript_subject_area.table.subject_area
    )
    if valid_version_ids is not None:
      query = query.filter(
        db.manuscript_subject_area.table.version_id.in_(valid_version_ids)
      )
    return ManuscriptSubjectAreaService.from_manuscript_version_id_subject_area_tuples(
      query.all()
    )

  @staticmethod
  def from_manuscript_version_id_subject_area_tuples(manuscript_version_id_subject_area_tuples):
    return ManuscriptSubjectAreaService(
      ids_by_subject_area_map=applymap_dict(groupby_to_dict(
        manuscript_version_id_subject_area_tuples,
        lambda x: x[1].lower(), lambda x: x[0]
      ), set),
      subject_areas_by_id_map=applymap_dict(groupby_to_dict(
        manuscript_version_id_subject_area_tuples,
        lambda x: x[0], lambda x: x[1]
      ), sorted),
      all_subject_areas=set(subject_area for _, subject_area in manuscript_version_id_subject_area_tuples)
    )

  def get_ids_by_subject_areas(self, subject_areas):
    return set(iter_flatten(
      self._ids_by_subject_area_map.get(subject_area.lower(), [])
      for subject_area in subject_areas
    ))

  def get_subject_areas_by_id(self, manuscript_version_id):
    return self._subject_areas_by_id_map.get(manuscript_version_id, [])

  def get_all_subject_areas(self):
    return self._all_subject_areas
