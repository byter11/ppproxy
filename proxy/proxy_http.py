from os import remove
import logging

buffer = 2048
log = logging.getLogger('proxy-logger')

def proxy_http(data, sock, conn, cache):
  filename = encoded(data[data.index('GET'):].split()[1])
  content = cache.get(filename)
  if content:
    log.info(f"Cache Hit: {filename}")
    conn.sendall(content)
    return

  is_good = False
  res = b''
  with open(filename, 'wb') as f:
    sock.send(str.encode(data))
    while True:
      reply = sock.recv(buffer)
      try:
        if '200 OK' in reply.decode():    # Only save in cache when connection OK
          is_good = True 
      except: pass
      res += reply
      if len(reply) <=  0: break
      conn.sendall(reply)
  if not is_good:
    remove(filename)
  else:
    cache.put(filename, res)

def encoded(url):
  return url.replace('http://', '').replace('/', '-').replace('?', '')