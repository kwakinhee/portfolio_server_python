from twisted.internet import reactor
from twisted.application import service
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from commonlib.netlib.http.server.router import Router
from configServer.restApiHandler.fetch import Fetch
from commonlib.glog import glog
# from commonlib.gconf import gconf
from commonlib.util.singleton import Singleton
from commonlib.configLoader import loadConfig
from typing import *


class ConfigService(service.Service, metaclass=Singleton):
    configData = None
    def __init__(self):
        super().__init__()
        if self.reload() is False:
            exit(1)

    def startService(self, application, mainName):
        super().startService()

        glog.info("start server")
        glog.Init(application)

        bindAddress: Final = "0.0.0.0"
        # configServerUrl: Final = gconf.serviceGroup.http.configServer.url
        port: Final = 20100

        # Register API + endpoints
        configApi = self.init_rest_api_server()

        if mainName == '__main__':
            reactor.listenTCP(port, configApi, interface=bindAddress)
            glog.info(f"API start listening ... http://{bindAddress}:{port}")
            # # 테스트용 bot client
            # reactor.connectTCP(bindAddres, port, GClientFactory(BotClient))

            reactor.run()
        else:
            pass
            # # tac 명령어를 이용한 서비스 그룹 실행.
            # serviceCollection = service.IServiceCollection(application)
            # internet.TCPServer(
            #     port,
            #     GServerFactory(Client)).setServiceParent(serviceCollection)

            # # 테스트용 bot client
            # internet.TCPClient(
            #     bindAddres, port,
            #     GClientFactory(BotClient)).setServiceParent(serviceCollection)

    def stopService(self, mainName):

        if reactor.running:
            reactor.removeAll()
            reactor.iterate()
            reactor.stop()

        super().stopService()

    def isRunniing(self):
        return True if self.running == 1 else False

    def init_rest_api_server(self):
        router = Router()
        router.register(r"^/fetch$", Fetch())
        return router

    def reload(self):
        serviceGroupCfg = loadConfig("service_group/", "dev.json5")
        self.configData = serviceGroupCfg
        