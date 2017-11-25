import unittest
import time

from data.src.SimpleSocket import SimpleSocket
from data.src.Client import Client
from data.src.Server import Server


class TestUM(unittest.TestCase):
    def setUp(self):
        self.server = Server("127.0.0.1", 1235, SimpleSocket.protTypeTCP)
        self.client = Client(SimpleSocket.protTypeTCP)
        self.client.connect("127.0.0.1", 1235)

    def test_simpleClientToServerCommunication(self):
        orgmsg = str(time.time()) * 10000

        self.client.toSend(orgmsg)
        time.sleep(2)
        buff = self.server.getClientBuffer(self.server.getClientObjPerTuple((self.client.ip, self.client.port)))
        self.assertEqual(buff, orgmsg)


if __name__ == '__main__':
    unittest.main()
