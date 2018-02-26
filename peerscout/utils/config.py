from configparser import ConfigParser

def dict_to_config(d):
  config = ConfigParser()
  for section in d.keys():
    config.add_section(section)
    for key, value in d[section].items():
      config.set(section, key, value)
  return config
