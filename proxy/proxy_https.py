from _thread import start_new_thread
import logging

buffer = 2048
log = logging.getLogger('proxy-logger')


def proxy_https(sock, conn):
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