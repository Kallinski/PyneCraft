import select
import _thread

from data.src.SimpleSocket import SimpleSocket


class Client(SimpleSocket):
    writeBuffer = ""
    serverIP = None
    serverPort = None

    def __init__(self, prot, sock=None, ip=None, port=None):
        super().__init__(ip, port, prot, sock)

    def connect(self, host, port):
        self.setBlocking(self.s, True)
        self.s.connect((host, port))
        self.serverIP = host
        self.serverPort = port

        self.port = self.s.getsockname()[1]
        self.ip = self.s.getsockname()[0]
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
