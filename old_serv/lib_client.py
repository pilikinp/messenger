import json
import time

# from lib_server import presence

def connect_guest(sock, account_name, status = 'Yep, I am here'):

    msg_client = {
        "action": 'presence',
        "time": time.time(),
        "type": 'status',
        "user": {
            'account_name': account_name,
            'status': status

        }
    }

    data = json.dumps(msg_client).encode()
    sock.send(data)

    msg_server = sock.recv(2048)
    msg_server = json.loads(msg_server.decode())
    print(msg_server)
    return msg_server