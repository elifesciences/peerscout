def normalise_subject_area(subject_area):
  return (
    subject_area.lower().title().replace(' And ', ' and ')
    if subject_area is not None
    else subject_area
  )
