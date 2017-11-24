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


class Server(SimpleSocket):
    clientsSockets = []
    clientsObj = []

    maxClients = 4

    def __init__(self, ip, port, prot=None, sock=None):
        super().__init__(ip, port, prot, sock)
        self.clientsSockets.append(self.s)
        self.bindAndListenSocket()
        self.thrd = _thread.start_new(self.__mainLoop, ())

    def bindAndListenSocket(self):
        self.s.bind((self.ip, self.port))
        self.s.listen(self.maxClients)

    def accept(self):

        print("new conn")

        clientSocket, clientAddress = self.s.accept()

        if str(clientSocket.type).find("SOCK_STREAM") != -1:
            newSocket = Client(SimpleSocket.protTypeTCP, clientSocket)
        elif clientSocket.type == "SocketKind.SOCK_DGRAM":
            newSocket = Client(SimpleSocket.protTypeUDP, clientSocket)
        else:
            raise Exception("Socket is from not supportet type " + str(clientSocket.type))

        self.clientsSockets.append(newSocket.s)
        self.clientsObj.append(newSocket)
        return (newSocket, clientAddress)

    def disconnectClient(self, client):
        self.clientsSockets.remove(client)

    def readFromClient(self, client):
        self.recv(client)

    def sendToClient(self, client, msg):
        client.send(msg)

    def __mainLoop(self):

        while True:
            readable, writable, exeptional = select.select(self.clientsSockets, self.clientsSockets,
                                                           self.clientsSockets)

            for s in readable:
                if s is self.s:
                    # here we have to handle a new connection
                    self.accept()
                else:
                    # here we can read from the sockets.
                    ser.readFromClient(s)


class Client(SimpleSocket):
    writeBuffer = ""

    def __init__(self, prot, sock=None, ip=None, port=None):
        super().__init__(ip, port, prot, sock)

    def connect(self, host, port):
        self.setBlocking(self.s, True)
        self.s.connect((host, port))
        self.setBlocking(self.s, False)
        self.thrd = _thread.start_new(self.__mainLoop, ())

    def select(self):
        readable, writable, exeptional = select.select([self.s], [self.s], [self.s])
        return (readable, writable, exeptional)

    def __mainLoop(self):

        while True:
            readable, writable, exeptional = select.select([self.s], [self.s], [self.s])

            if self.s in readable:
                self.recv(self.s)

            if self.s in writable and len(self.writeBuffer) != 0:
                sended = self.send(self.s, self.writeBuffer)
                self.writeBuffer = self.writeBuffer[sended + 1:]

    def toSend(self, msg):
        self.writeBuffer += str(msg)


ser = Server("127.0.0.1", 1235, SimpleSocket.protTypeTCP)

c = Client(SimpleSocket.protTypeTCP)

c.connect("127.0.0.1", 1235)

while True:
    c.toSend(time.time())
    time.sleep(2)
