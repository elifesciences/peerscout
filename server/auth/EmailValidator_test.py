from io import StringIO

from .EmailValidator import (
  read_valid_emails_from_fp,
  parse_valid_domains,
  EmailValidator
)

class TestReadValidEmailsFromFp(object):
  def test_should_read_emails_as_lower_case(self):
    emails = read_valid_emails_from_fp(StringIO('User1@Domain.Org'))
    assert emails == {'user1@domain.org'}

  def test_should_read_multiple_emails(self):
    emails = read_valid_emails_from_fp(StringIO('user1@domain.org\nuser2@domain.org'))
    assert emails == {'user1@domain.org', 'user2@domain.org'}

  def test_should_ignore_blank_lines(self):
    emails = read_valid_emails_from_fp(StringIO('user1@domain.org\n\n\nuser2@domain.org'))
    assert emails == {'user1@domain.org', 'user2@domain.org'}

  def test_should_ignore_space_around_emails(self):
    emails = read_valid_emails_from_fp(StringIO(' user1@domain.org \n user2@domain.org '))
    assert emails == {'user1@domain.org', 'user2@domain.org'}


class TestParseDomains(object):
  def test_should_parse_domains_as_lower_case(self):
    domains = parse_valid_domains('Domain.Org')
    assert domains == {'domain.org'}

  def test_parse_multiple_emails(self):
    domains = parse_valid_domains('domain1.org,domain2.org')
    assert domains == {'domain1.org', 'domain2.org'}

  def test_should_ignore_blank_domains(self):
    domains = parse_valid_domains('domain1.org,,domain2.org')
    assert domains == {'domain1.org', 'domain2.org'}

  def test_should_ignore_space_around_domains(self):
    domains = parse_valid_domains(' domain1.org , domain2.org ')
    assert domains == {'domain1.org', 'domain2.org'}

class TestEmailValidator(object):
  def test_should_return_false_if_email_is_none(self):
    validator = EmailValidator(valid_emails={'user1@domain.org'})
    assert not validator(None)

  def test_should_return_false_if_email_not_in_list(self):
    validator = EmailValidator(valid_emails={'user1@domain.org'})
    assert not validator('other@domain.org')

  def test_should_return_true_if_email_in_list(self):
    validator = EmailValidator(valid_emails={'user1@domain.org'})
    assert validator('user1@domain.org')

  def test_should_return_true_if_email_in_list_with_different_case(self):
    validator = EmailValidator(valid_emails={'user1@domain.org'})
    assert validator('User1@Domain.org')

  def test_should_return_false_if_domain_not_in_list(self):
    validator = EmailValidator(valid_domains={'domain.org'})
    assert not validator('user1@other.org')

  def test_should_return_true_if_email_domain_in_list(self):
    validator = EmailValidator(valid_domains={'domain.org'})
    assert validator('user1@domain.org')

  def test_should_return_true_if_email_domain_in_list_with_different_case(self):
    validator = EmailValidator(valid_domains={'domain.org'})
    assert validator('User1@Domain.org')
