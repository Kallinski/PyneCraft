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
