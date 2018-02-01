import json
import unittest
from unittest.mock import Mock
import time

import lib_server
import lib_client


class CtestLibServer(unittest.TestCase):

    def test_presence(self):
        account_name = 'pilik'
        virt_sock = Mock()
        virt_sock.send.return_value = None
        result = lib_server.presence(virt_sock, account_name)
        self.assertEqual(result['responce'], '200')
        self.assertEqual(result['allert'], 'Connection')
        result = lib_server.presence(virt_sock, account_name)
        self.assertEqual(result['responce'], '409')
        self.assertEqual(result['allert'], 'Conflict')

    def test_connect_guest(self):
        msg_server = {
            'responce': '200',
            'time': time.time(),
            'allert': 'Connection'
        }
        data = json.dumps(msg_server).encode()
        virt_sock = Mock()
        virt_sock.send.return_value = None
        virt_sock.recv.return_value = data
        result = lib_client.connect_guest(virt_sock, 'pilik')
        self.assertEqual(msg_server, result)