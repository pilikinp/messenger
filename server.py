from lib_server import main_loop


# server_sock = socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM, proto = 0) # TCP
# server_sock.bind(("", 7771))
# server_sock.listen(5)




# while True:
#     sock, addr = server_sock.accept()
#     msg = sock.recv(2048)
#     msg = json.loads(msg.decode())
#     commands[msg['action']](sock, msg['user']['account_name'], msg['user']['status'])





main_loop()