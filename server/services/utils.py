import html
from html.parser import HTMLParser

class MLStripper(HTMLParser):
  def __init__(self):
    super().__init__()
    self.reset()
    self.strict = False
    self.convert_charrefs = True
    self.fed = []

  def handle_data(self, d):
    self.fed.append(d)

  def get_data(self):
    return ''.join(self.fed)

  def error(self, err):
    raise err

def strip_tags(text):
  s = MLStripper()
  s.feed(text)
  return s.get_data()

def unescape_and_strip_tags(text):
  return strip_tags(html.unescape(text))
