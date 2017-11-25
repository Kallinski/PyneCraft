import select
import _thread

from data.src.SimpleSocket import SimpleSocket
from data.src.Client import Client


class Server(SimpleSocket):
    clientsSockets = []
    clientsSoToObj = {}

    clientReadBuffer = {}

    maxClients = 4

    def __init__(self, ip, port, prot=None, sock=None):
        super().__init__(ip, port, prot, sock)
        self.clientsSockets.append(self.s)
        self.bindAndListenSocket()
        self.thrd = _thread.start_new(self.__mainLoop, ())

    def bindAndListenSocket(self):
        self.s.bind((self.ip, self.port))
        self.s.listen(self.maxClients)

    def addNewClient(self, clientObj):
        self.clientReadBuffer[clientObj] = ""
        self.clientsSockets.append(clientObj.s)
        self.clientsSoToObj[clientObj.s] = clientObj

    def getClientObjPerTuple(self, ipPortTuple):
        (ip, port) = ipPortTuple
        for s in self.clientsSockets:
            if s == self.s:
                # skipp server
                continue
            if (self.clientsSoToObj[s].ip == ip) and (self.clientsSoToObj[s].port == port):
                return self.clientsSoToObj[s]
        return None

    def getClientBuffer(self, client):
        msg = self.clientReadBuffer[client]
        self.clientReadBuffer[client] = ""
        return msg

    def accept(self):

        clientSocket, clientAddress = self.s.accept()

        if str(clientSocket.type).find("SOCK_STREAM") != -1:
            newSocket = Client(SimpleSocket.protTypeTCP, clientSocket)
        elif clientSocket.type == "SocketKind.SOCK_DGRAM":
            newSocket = Client(SimpleSocket.protTypeUDP, clientSocket)
        else:
            raise Exception("Socket is from not supportet type " + str(clientSocket.type))

        (newSocket.ip, newSocket.port) = clientAddress
        self.addNewClient(newSocket)
        return (newSocket, clientAddress)

    def disconnectClient(self, client):
        self.clientsSockets.remove(client)

    def readFromClient(self, client):
        msg = self.recv(client.s)
        self.clientReadBuffer[client] += msg

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
                    self.readFromClient(self.clientsSoToObj[s])
