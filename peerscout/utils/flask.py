from functools import wraps

def no_cache(f):
  @wraps(f)
  def wrapper():
    response = f()
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    return response
  return wrapper
