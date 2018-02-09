import threading

def lazy_thread_local(constructor):
  data = threading.local()
  def lazy_getter():
    try:
      return data.value
    except AttributeError:
      data.value = constructor()
      return data.value
  return lazy_getter
