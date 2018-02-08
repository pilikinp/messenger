import sys
import socketserver
import json

from old_serv.lib_server import presence

if len(sys.argv) == 1:
    adr = ''
    port = 7777
else:
    adr, port = sys.argv[1], int(sys.argv[2])


class CHandler(socketserver.BaseRequestHandler):

    def handle(self):

        commands = {
            'presence': presence
        }


        msg = self.request.recv(2048)
        msg = json.loads(msg.decode())
        commands[msg['action']](self, msg['user']['account_name'])



with socketserver.TCPServer((adr , port), CHandler) as server:

    server.serve_forever()