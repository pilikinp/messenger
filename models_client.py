import time, sys
import socket
import threading, queue
import hashlib

from models import JimMessage, JimAnswer
from models_repository_client import Repository, Contacts, HistoryMessage

import crypt


class Client():
    username = ''
    msg_client = JimMessage()
    msg_server = JimAnswer()

    def __init__(self, host, port):
        self._host = host
        self._port = port
        self.lock = threading.Lock()
        self.recv_queue = queue.Queue()
        self.secret = 'secretkey'

    @property
    def socket(self):
        return self._sock

    def connect_guest(self, action, password):
        pas = hashlib.sha256()
        pas.update(self.username.encode())
        pas.update(password.encode())
        pas.update(self.secret.encode())
        password = pas.hexdigest()
        if action == 'registration':
            publickey = crypt.create_rsa(self.username)
        else:
            publickey = crypt.get_publickey(self.username)
        data = {'action': action,
                'time': time.ctime(),
                'user': self.username,
                'password': password,
                'publickey': publickey}
        self.socket.send(self.msg_client.pack(data))
        print('сообщение отправлено')
        msg_recv = self.socket.recv(1024)
        msg_recv = self.msg_server.unpack(msg_recv)
        print(msg_recv)
        if msg_recv['response'] == '102':
            print(msg_recv['alert'])
            self.rep = Repository(self.username)
            self.msg()
            print('запускаю получение контактов')
            self.get_contact_list(self.socket)
            time.sleep(0.2)
            self.get_chat_list()
        elif msg_recv['response'] == '201':
            print(msg_recv['alert'])
            print('Вы зарегистрировались под ником {}'.format(self.username))
            self.rep = Repository(self.username)
            self.msg()
            # self.get_contact_list(self.socket)
        # else:
        #     print('Возникла ошибка {} обратитесь к справке или напишите в поддержку'.format(msg_recv['response']))
        self.recv_queue.put(msg_recv)

    def reg_guest(self):
        data = {'action': 'registration',
                'time': time.ctime(),
                'user': self.username}
        self.socket.send(self.msg_client.pack(data))
        msg_recv = self.socket.recv(1024)
        msg_recv = self.msg_server.unpack(msg_recv)
        print(msg_recv)
        if msg_recv['response'] == '201':
            print(msg_recv['alert'])
            print('Вы зарегистрировались под ником {}'.format(self.username))
            self.rep = Repository(self.username)
        else:
            print('Возникла ошибка {} обратитесь к справке или напишите в поддержку'.format(msg_recv['response']))
            sys.exit()

    def add_chat(self, chat_name):
        sock = self.socket
        msg = {'action': 'add_chat',
                'time': time.ctime(),
               'chat': chat_name}
        self.msg_client.pack(msg)
        sock.send(msg)


    def add_contact(self, contact):
        sock = self.socket
        msg = {'action': 'add_contact',
               'time': time.ctime(),
               'user': self.username,
               'contact': contact}
        msg = self.msg_client.pack(msg)
        sock.send(msg)

    def del_contact(self, contact):
        sock = self.socket
        msg = {'action': 'del_contact',
               'time': time.ctime(),
               'user': self.username,
               'contact': contact}
        msg = self.msg_client.pack(msg)
        sock.send(msg)

    def get_contact_list(self, *args):
        # cont_l = []
        sock = args[0]
        self.rep.del_model(Contacts)
        msg = {'action': 'get_contact_list',
                          'time': time.ctime(),
                          'user': self.username}
        msg = self.msg_client.pack(msg)
        sock.send(msg)
        print('get_contacts')

    def search_contact(self, text):
        # некоректно работает поиск, требуется переделать!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        data = {'users': []}
        sock = self.socket
        for contact in self.rep.contacts_list():
            if text.lower() in contact.contact_name.lower():
                data['users'].append(contact.contact_name)
        if data['users']:
            self.recv_queue.put(data)
        else:
            msg = {'action': 'search_contact',
                   'contact': text}
            msg = self.msg_client.pack(msg)
            time.sleep(0.2)
            sock.send(msg)


    def get_chat_list(self):
        sock = self.socket
        msg = {'action': 'get_chat_list',
               'time': time.ctime(),
               'user': self.username}
        msg = self.msg_client.pack(msg)
        sock.send(msg)

    def exit(self, *args):
        sock = args[0]
        msg = self.msg_client.msg('exit', self.username)
        msg = self.msg_client.pack(msg)
        sock.send(msg)
        sys.exit()

    def _send_message(self, *args):
        sock, to_, message, username, flag = args
        sessionkey = ''
        signature = ''
        self.rep.add_obj(HistoryMessage(time.ctime(), username, to_, message))
        if flag:
            publickey = self.rep.get_publickey(to_)
            data = crypt.create_msg(message, self.username, publickey)
            print(data)
            message = data['message']
            sessionkey = data['session key']
            # signature = data['signature']
        msg = {'action': 'msg',
               'time': time.ctime(),
               'to': to_,
               'from': username,
               'message': message,
               'session key': sessionkey,
               # 'signature': signature,
               'flag': flag}
        # self.rep.add_obj(HistoryMessage(msg['time'], msg['from'], msg['to'], msg['message']))
        msg = self.msg_client.pack(msg)
        sock.send(msg)


    def _get_message(self):
        sock = self.socket
        cont_l = []
        while True:
            try:
                sock.settimeout(2)
                data = sock.recv(2048)
                data = self.msg_server.unpack(data)
                print(data)
                if 'action' in data:
                    if data['action'] == 'msg' and data['flag']:
                        dec = crypt.decript_msg(data, self.username)
                        data['message'] = dec.decode()
                        self.rep.add_obj(HistoryMessage(data['time'], data['from'], data['to'], data['message']))
                    else:
                        print(data['time'], data['from'], data['message'])
                        self.rep.add_obj(HistoryMessage(data['time'], data['from'], data['to'], data['message']))
                elif 'response' in data:
                    print(data['response'], data['time'], data['alert'])
                elif 'users' in data:
                    print('Кол-во контактов: ',len(data['users']))
                    # for cont in data['users']:
                    #     self.rep.add_contact(cont)
                    for name, publickey in data['users'].items():
                        self.rep.add_contact(name, publickey)
                    self.rep.session.commit()
                elif 'found_users' in data:
                    data['users'] = data['found_users']
                self.recv_queue.put(data)
            except socket.timeout:
                pass

    def msg(self):
        t2 = threading.Thread(target=self._get_message)
        t2.daemon = True
        t2.start()

    def login_chat(self, *args):
        sock = args[0]
        data = self.action(sock,'login_chat')
        if data['response'] == '200':
            self.chat(sock)
        else:
            print(data)

    def chat(self, *args):
        sock = args[0]
        t1 = threading.Thread(target=self._send_message, args=(sock, 'chat'))
        t2 = threading.Thread(target=self._get_message, args=(sock,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    def run(self, name, password, action):
        self.username = name
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self._host, self._port))
        self.connect_guest(action, password)




# что за ошибка JSONDecodeError("Extra data", s, end)