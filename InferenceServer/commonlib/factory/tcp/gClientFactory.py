from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory, ReconnectingClientFactory
from typing import *
from commonlib.glog import glog


#클라이언트 객체 생성
class GClientFactory(ClientFactory):
    def __init__(self, clientprotocol):
        self.client = None
        self.protocol = clientprotocol

    def buildProtocol(self, addr):
        glog.info('[Bot] connected')
        self.client = self.protocol(self)
        return self.client

    def clientConnectionFailed(self, connector, reason):
        glog.info("[Bot] connection failed: {}".format(
            reason.getErrorMessage()))

    def clientConnectionLost(self, connector, reason):
        glog.info("[Bot] clientConnectionLost: {}".format(
            reason.getErrorMessage()))

    def startedConnecting(self, connector):
        glog.info('[Bot] started connecting..')

    #서버 접속
    def connectServer(self):
        reactor.connectTCP('127.0.0.1', 10001, self)
