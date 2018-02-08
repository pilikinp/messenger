import sys
import socket

from old_serv.lib_client import connect_guest

if len(sys.argv) == 1:
    adr = '127.0.0.1'
    port = 7777
else:
    adr, port = sys.argv[1], int(sys.argv[2])

sock = socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM, proto= 0)
sock.connect((adr, port))

connect_guest(sock, 'pilik')

