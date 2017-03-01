import requests

def main():
  try:
    response = requests.post('http://localhost:8080/control/reload')
    response.raise_for_status()
    print("response:", response.text)
  except requests.exceptions.ConnectionError:
    print("server doesn't seem to be running")
  print("done")

if __name__ == "__main__":
  main()
