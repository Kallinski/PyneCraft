import socket
import select
import time
import _thread


class SimpleSocket(object):
    protTypeUDP = socket.SOCK_DGRAM
    protTypeTCP = socket.SOCK_STREAM

    ip = None
    port = None

    s = None
    thrd = None

    def __init__(self, ip, port, prot=None, sock=None):
        self.ip = ip
        self.port = port
        if sock == None:
            self.s = self.createSocket(prot)
        else:
            self.s = sock

        self.setBlocking(self.s, False)

    @staticmethod
    def createSocket(protocol):
        assert (protocol == socket.SOCK_DGRAM or protocol == socket.SOL_SOCKET)
        sock = socket.socket(socket.AF_INET, protocol)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock

    @staticmethod
    def close(sock):
        sock.close()

    @staticmethod
    def setBlocking(sock, setter):
        sock.setblocking(setter)

    @staticmethod
    def send(sock, msg):
        return sock.send(b'' + str(msg).encode())

    @staticmethod
    def recv(sock):
        msg = sock.recv(4069)
        print(msg)
        return msg

    def select(self):
        pass

    def __mainLoop(self):
        pass
