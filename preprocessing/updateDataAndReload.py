from importlib import import_module

def main():
  scripts = [
    'convertFiles',
    'convertEarlyCareerResearchersCsv',
    'postProcessFiles',
    'enrichEarlyCareerResearchers',
    'generateSense2VecTokens',
    'generateSense2VecLdaDocVec',
    'generateSense2VecDoc2Vec',
    'reloadServer'
  ]
  if not import_module('downloadFiles').main():
    print("no files downloaded, skipping further processing")
    return False
  for script in scripts:
    print("running:", script)
    pkg = import_module(script)
    pkg.main()
  print("done")
  return True

if __name__ == "__main__":
  main()
