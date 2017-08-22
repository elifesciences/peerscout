
def read_valid_emails_from_fp(fp):
  return set([s.strip().lower() for s in fp.readlines()]) - {''}

def read_valid_emails(valid_emails_filename):
  with open(valid_emails_filename, 'r') as valid_emails_f:
    return read_valid_emails_from_fp(valid_emails_f)

def parse_valid_domains(valid_domains):
  valid_domains = valid_domains.strip() if valid_domains else ''
  if not valid_domains:
    return None
  return {s.strip().lower() for s in valid_domains.split(',')} - {''}

def email_to_domain(email):
  if email:
    parts = email.split('@')
    if len(parts) == 2:
      return parts[1]
  return None

def EmailValidator(valid_emails=None, valid_email_domains=None):
  if valid_emails is None:
    valid_emails = set()
  if valid_email_domains is None:
    valid_email_domains = set()

  def validate(email):
    if not email:
      return False
    domain = email_to_domain(email)
    return (
      (domain and domain.lower() in valid_email_domains) or
      (email.lower() in valid_emails)
    )
  return validate
