from sqlalchemy import (
  Column,
  Boolean,
  DateTime,
  Integer,
  Interval,
  String
)
from sqlalchemy.ext.declarative import declarative_base

def compile_minutes_duration(dialect, minutes):
  if dialect == 'postgresql':
    return "INTERVAL 'P0Y0M0DT0H{}M0S'".format(minutes)
  elif dialect == 'sqlite':
    return str(minutes * 60)
  else:
    raise Exception("unsupported dialect: {}".format(dialect))

def compile_years_duration(dialect, years):
  if dialect == 'postgresql':
    return "INTERVAL 'P{}Y0M0DT0H0M0S'".format(years)
  elif dialect == 'sqlite':
    return str(years * 60 * 60 * 24 * 12)
  else:
    raise Exception("unsupported dialect: {}".format(dialect))

def compile_duration_days(dialect, expr_from, expr_to):
  SECONDS_IN_DAY = 24 * 60 * 60
  if dialect == 'postgresql':
    return "(extract(epoch from {} - {})/{})".format(expr_to, expr_from, SECONDS_IN_DAY)
  elif dialect == 'sqlite':
    return "(julianday({}) - julianday({}))".format(expr_to, expr_from)
  else:
    raise Exception("unsupported dialect: {}".format(dialect))

def create_views(dialect):
  Base = declarative_base()

  min_duration = compile_minutes_duration(dialect, 1)
  one_year = compile_years_duration(dialect, 1)

  class ManuscriptPersonReviewTimes(Base):
    __tablename__ = "manuscript_person_review_times"

    version_id = Column(String, primary_key=True)
    person_id = Column(String, primary_key=True)

    contacted_timestamp = Column(DateTime)

    accepted_timestamp = Column(DateTime)
    accepted_duration = Column(Interval)

    declined_timestamp = Column(DateTime)
    declined_duration = Column(Interval)

    reviewed_timestamp = Column(DateTime)
    reviewed_duration = Column(Interval)

    accepted_declined = Column(Boolean)
    awaiting_accept = Column(Boolean)
    awaiting_review = Column(Boolean)

    __query__ =\
    """
    select
      mv.version_id,
      ms_contacted.person_id,
      min(ms_contacted.stage_timestamp) contacted_timestamp,
      min(ms_accepted.stage_timestamp) accepted_timestamp,
      {accepted_duration_days} accepted_duration,
      min(ms_declined.stage_timestamp) declined_timestamp,
      {declined_duration_days} declined_duration,
      min(ms_reviewed.stage_timestamp) reviewed_timestamp,
      {reviewed_duration_days} reviewed_duration,
      (
        min(ms_accepted.stage_timestamp) is not null and
        min(ms_declined.stage_timestamp) is not null and
        min(ms_reviewed.stage_timestamp) is null
      ) accepted_declined,
      (
        min(ms_accepted.stage_timestamp) is null and
        min(ms_declined.stage_timestamp) is null and
        min(ms_reviewed.stage_timestamp) is null
      ) awaiting_accept,
      (
        min(ms_accepted.stage_timestamp) is not null and
        min(ms_declined.stage_timestamp) is null and
        min(ms_reviewed.stage_timestamp) is null
      ) awaiting_review
    from manuscript_version mv
    join manuscript_stage ms_contacted
      on ms_contacted.version_id = mv.version_id
      and ms_contacted.stage_name = 'Contacting Reviewers'
    left outer join manuscript_stage ms_accepted
      on ms_accepted.version_id = mv.version_id
      and ms_accepted.person_id = ms_contacted.person_id
      and ms_accepted.stage_timestamp >= ms_contacted.stage_timestamp + {min_duration}
      and ms_accepted.stage_name = 'Reviewers Accept'
    left outer join manuscript_stage ms_declined
      on ms_declined.version_id = mv.version_id
      and ms_declined.person_id = ms_contacted.person_id
      and ms_declined.stage_timestamp >= ms_contacted.stage_timestamp + {min_duration}
      and ms_declined.stage_name = 'Reviewers Decline'
    left outer join manuscript_stage ms_reviewed
      on ms_reviewed.version_id = mv.version_id
      and ms_reviewed.person_id = ms_contacted.person_id
      and ms_reviewed.stage_timestamp >= ms_contacted.stage_timestamp + {min_duration}
      and ms_reviewed.stage_name = 'Review Received'
    group by mv.version_id, ms_contacted.person_id
    """.format(
      accepted_duration_days=compile_duration_days(
        dialect,
        'min(ms_contacted.stage_timestamp)',
        'min(ms_accepted.stage_timestamp)'
      ),
      declined_duration_days=compile_duration_days(
        dialect,
        'min(ms_contacted.stage_timestamp)',
        'min(ms_declined.stage_timestamp)'
      ),
      reviewed_duration_days=compile_duration_days(
        dialect,
        'min(ms_accepted.stage_timestamp)',
        'min(ms_reviewed.stage_timestamp)'
      ),
      min_duration=min_duration
    )

  class PersonReviewStatsMixin(object):
    person_id = Column(String, primary_key=True)

    accepted_duration_min = Column(Interval)
    accepted_duration_max = Column(Interval)
    accepted_duration_avg = Column(Interval)
    accepted_count = Column(Integer)

    declined_duration_min = Column(Interval)
    declined_duration_max = Column(Interval)
    declined_duration_avg = Column(Interval)
    declined_count = Column(Integer)

    reviewed_duration_min = Column(Interval)
    reviewed_duration_max = Column(Interval)
    reviewed_duration_avg = Column(Interval)
    reviewed_count = Column(Integer)

    accepted_declined_count = Column(Integer)
    awaiting_accept_count = Column(Integer)
    awaiting_review_count = Column(Integer)

  _BASE_REVIEW_STATS_QUERY =\
  """
  select
    person_id,

    count(contacted_timestamp) as contacted_count,

    min(accepted_duration) as accepted_duration_min,
    max(accepted_duration) as accepted_duration_max,
    avg(accepted_duration) as accepted_duration_avg,
    count(accepted_duration) as accepted_count,

    min(declined_duration) as declined_duration_min,
    max(declined_duration) as declined_duration_max,
    avg(declined_duration) as declined_duration_avg,
    count(declined_duration) as declined_count,

    min(reviewed_duration) as reviewed_duration_min,
    max(reviewed_duration) as reviewed_duration_max,
    avg(reviewed_duration) as reviewed_duration_avg,
    count(reviewed_duration) as reviewed_count,

    count(case when accepted_declined then 1 end) as accepted_declined_count,
    count(case when awaiting_accept then 1 end) as awaiting_accept_count,
    count(case when awaiting_review then 1 end) as awaiting_review_count
  from manuscript_person_review_times
  """

  class PersonReviewStatsOverall(PersonReviewStatsMixin, Base):
    __tablename__ = "person_review_stats_overall"

    __query__ =\
    _BASE_REVIEW_STATS_QUERY +\
    """
    group by person_id
    """

  class PersonReviewStatsLast12m(PersonReviewStatsMixin, Base):
    __tablename__ = "person_review_stats_last12m"

    __query__ =\
    _BASE_REVIEW_STATS_QUERY +\
    """
    where contacted_timestamp >= (current_date - {interval})
    group by person_id
    """.format(interval=one_year)

  return [
    ManuscriptPersonReviewTimes,
    PersonReviewStatsOverall,
    PersonReviewStatsLast12m
  ]
