from twisted.internet.protocol import ServerFactory


class GServerFactory(ServerFactory):
    def __init__(self, protocol):
        self.protocol = protocol

    def buildProtocol(self, addr):
        # print('connected')
        self.addr = addr
        self.client = self.protocol(self)
        return self.client
