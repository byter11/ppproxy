from os import remove
import socket
import sys, time, logging
from logging.handlers import RotatingFileHandler
from _thread import *
from os.path import exists
from cache import Cache, Schedule

PORT = 8000
buffer = 2048

handler = RotatingFileHandler('proxy.log', mode='a', maxBytes=1024*5, backupCount=1)
log = logging.getLogger(__name__)
log.addHandler(handler)
log.setLevel(logging.INFO)
cache = Cache(Schedule.LRU)

def start():
  try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', PORT))
    sock.listen(10)
    sock.settimeout(5)
    log.info("[*] Server started successfully [ %d ]" %(PORT))
  except Exception as e:
    log.error("[*] Unable to Initialize Socket")
    log.error(e)
    sys.exit(2)

  while True:
    try:
      conn, addr = sock.accept() #Accept connection from client browser
      conn.settimeout(5)
      data = conn.recv(buffer) #Recieve client data
      start_new_thread(proxy, (data, sock, conn, addr)) #Starting a thread
    except socket.timeout: pass
    except KeyboardInterrupt:
      sock.close()
      log.info("\n[*] Graceful Shutdown")
      sys.exit(1)

def proxy_http(data, sock, conn):
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


def proxy_https(server, sock, conn):
  response = "HTTP/1.1 200 Connection Established\r\nProxy-Agent: tcpServer\r\n\r\n"
  conn.send(str.encode(response)) # Initiate SSL handshake
  start_new_thread(client_to_server, (conn, sock))

  bytes = 0
  while True:
    try:
      reply = sock.recv(buffer)   # Receive from server
      bytes += len(reply)
      conn.send(reply)            # Forward to client
      if len(reply) <= 0:
        break  
    except Exception as e:
      log.debug(f'proxy_https: {e}')
      break
  
def proxy(data, sock, conn, addr):
  try: data = data.decode('utf-8')
  except: return
  
  # Extract web server
  i = data.find('Host: ')
  webserver = data[i:].split('\n')[0][6:].strip().split(':')

  # Find port
  if len(webserver) == 1:
    name, port = webserver[0], "80"
  elif len(webserver) == 2:
    name, port = webserver
  else: return

  log.info(f'{addr} | {name}:{port}')
  ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  ip = socket.gethostbyname(name)
  try:
    ssock.connect((ip, int(port)))
  except Exception as e: 
    log.debug(f'sock.connect: {e}')
    ssock.close()
    return
  
  if port == "80":
    proxy_http(data, ssock, conn)
  else:
    proxy_https(name, ssock, conn)

  ssock.close()
  conn.close()

def client_to_server(conn, sock):
  while True:
    try:
      data = conn.recv(buffer)  # Receive from client
      sock.send(data)           # Forward to server
      if len(data) <= 0:
        break
    except Exception as e:
      log.debug(f'client_to_server: {e}')
      conn.close()
      sock.close()
      return

def fetch_file(filename):
  if not exists(filename):
    return

  with open(filename, 'rb') as f:
    return f.read()

def encoded(url):
  return url.replace('http://', '').replace('/', '-').replace('?', '')

if __name__== "__main__":
    start()