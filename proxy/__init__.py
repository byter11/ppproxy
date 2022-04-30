from os import remove
import socket
import sys, time, logging
from logging.handlers import RotatingFileHandler
from _thread import *
from os.path import exists
from models import Filter
from .proxy_http import proxy_http
from .proxy_https import proxy_https
from models import Filter

PORT = 8000
buffer = 2048

handler = RotatingFileHandler('proxy.log', mode='a', maxBytes=1024*5, backupCount=1)
log = logging.getLogger('proxy-logger')
log.addHandler(handler)
log.setLevel(logging.INFO)

def start(cache, app):
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
      start_new_thread(proxy, (data, conn, addr, cache, app)) #Starting a thread
    except socket.timeout: pass
    except KeyboardInterrupt:
      sock.close()
      log.info("\n[*] Graceful Shutdown")
      sys.exit(1)

def proxy(data, conn, addr, cache, app):
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

  with app.app_context():
    query = Filter.query.filter(Filter.site.contains(name)).first()
    print(query)
    if query:
      log.info(f'Filtered {name} (rule: {query.name})')
      return
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
    proxy_http(data, ssock, conn, cache)
  else:
    proxy_https(ssock, conn)

  ssock.close()
  conn.close()