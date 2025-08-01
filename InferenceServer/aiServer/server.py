from twisted.internet import task, reactor
from twisted.application import internet, service
from twisted.application.service import Application
import sys, os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from commonlib.factory.tcp.gServerFactory import GServerFactory
from commonlib.factory.tcp.gClientFactory import GClientFactory
from commonlib.glog import glog
from commonlib.gconf import gconf
from commonlib.util.singleton import Singleton
from commonlib.netlib.http.client.configClient import ConfigApiClientSync as ConfigClient
from typing import *
from client import Client
from clientMgr import ClientMgr
from aiFacade import AiFacade
from time import sleep


class AiService(service.Service, metaclass=Singleton):
    def __init__(self):
        super().__init__()
        self.__tickTask: task.LoopingCall = None

    def startService(self, application, mainName):
        super().startService()

        glog.info("start server")
        glog.Init(application)

        # fetch Server Configuration 테스트 코드
        configClient = ConfigClient("http://config-server-config-inference-server:20100")
        configClient.fetch_config()
        glog.info("Initializing AI Facade")
        AiFacade().init()

        # client update tick
        fps: int = 30
        time_per_frame: float = 1 / fps
        self.__tickTask: task.LoopingCall = task.LoopingCall(
            ClientMgr().clientTick)
        self.__tickTask.start(time_per_frame)

        bindAddres: Final = gconf.serviceGroup.socketServer.bindAddress
        port: Final = gconf.serviceGroup.socketServer.port

        if mainName == '__main__':
            reactor.listenTCP(port, GServerFactory(Client))

            # 테스트용 bot client
            # reactor.connectTCP(bindAddres, port, GClientFactory(BotTCPClient))

            reactor.run()
        else:

            # tac 명령어를 이용한 서비스 그룹 실행.
            serviceCollection = service.IServiceCollection(application)
            internet.TCPServer(
                port,
                GServerFactory(Client)).setServiceParent(serviceCollection)

            # 테스트용 bot client
            # internet.TCPClient(
            #     bindAddres, port,
            #     GClientFactory(BotClient)).setServiceParent(serviceCollection)

    def stopService(self, mainName):

        if self.__tickTask == None:
            return

        self.__tickTask.stop()

        if reactor.running:
            reactor.removeAll()
            reactor.iterate()
            reactor.stop()

        super().stopService()

    def isRunniing(self):
        return True if self.running == 1 else False
