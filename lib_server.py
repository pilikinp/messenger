import json, time

clients = []
msg_server = {
    'responce': '',
    'time': time.time(),
    'allert': ''
}

def presence(self, account_name, status):

    if account_name in clients:
        msg_server['responce'] = '409'
        msg_server['allert'] = 'Conflict'
        data = json.dumps(msg_server).encode()
        self.request.send(data)

    else:
        msg_server['responce'] = '200'
        msg_server['allert'] = 'Connection'
        clients.append(account_name)
        data = json.dumps(msg_server).encode()
        self.request.send(data)


def quit(self, account_name):
    pass