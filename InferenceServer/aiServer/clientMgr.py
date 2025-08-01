from typing import *

from commonlib.glog import glog
from commonlib.util.singleton import Singleton
from datetime import datetime
from commonlib.util.gutil import curTimeUtc
import traceback
from aiFacade import AiFacade

if TYPE_CHECKING:
    from client import Client


#서버 접속한 Client session 관리.
class ClientMgr(metaclass=Singleton):
    def __init__(self):

        # tcp connected clients
        self.__reservedConnId: Set[int] = set()
        self.__clientsByConnId: Dict[int, Client] = {}

        # tcp logged in clients
        self.__clientsByClientId: Dict[int, Client] = {}
        self.__clientsByClientToken: Dict[str, Client] = {}

        self.__cachedClientIdsByClientToken: Dict[str, Client] = {}

        self.__increasedClientId: int = 0

        self.__createReservedConnId(1, 10)
        
        # ai 로직.
        self.__aiFacade: AiFacade = AiFacade()

    def __createReservedConnId(self, startConnId: int, endConnId: int):
        for x in range(int(startConnId), (int(endConnId) + 1)):
            self.__reservedConnId.add(x)

    def popReservedConnId(self):
        return self.__reservedConnId.pop()

    def __addReservedConnId(self, connId: int):
        return self.__reservedConnId.add(connId)

    def addClient(self, connId: int, client):
        self.__clientsByConnId[connId] = client

    def __removeClient(self, connId: int):
        del self.__clientsByConnId[connId]

    def getClient(self, connId: int):
        return self.__clientsByConnId[connId]

    def addLoggedInClient(self, client):
        clientId: int = client.getClientId()
        if clientId in self.__clientsByClientId:
            glog.error(
                "duplicate client (addLoggedInclient) clientId: {}".format(
                    clientId))
            return

        self.__clientsByClientId[clientId] = client
        clientToken: str = client.getClientToken()
        self.__clientsByClientToken[clientToken] = client

    def removeLoggedInClient(self, clientId: int, clientToken: str):
        if clientId in self.__clientsByClientId:
            del self.__clientsByClientId[clientId]

        if clientToken in self.__clientsByClientToken:
            del self.__clientsByClientToken[clientToken]

    def getClientByClientId(self, clientId: int):
        if clientId in self.__clientsByClientId:
            return self.__clientsByClientId[clientId]
        else:
            return

    def getClientByClientToken(self, clientToken: str):
        if clientToken in self.__clientsByClientToken:
            return self.__clientsByClientToken[clientToken]
        else:
            return

    # 추후 DB 연동시 삭제 예정 ----------------------------------
    def getClientIdByClientToken(self, clientToken: str):
        clientId: int = 0
        if clientToken in self.__cachedClientIdsByClientToken:
            clientId = self.__cachedClientIdsByClientToken[clientToken]
        else:
            clientId = self._generateClientId()
            self.__cachedClientIdsByClientToken[clientToken] = clientId

        return clientId

    def _generateClientId(self):
        self.__increasedClientId = self.__increasedClientId + 1
        return self.__increasedClientId

    # --------------------------------------------------------

    def broadCastPacket(self, data):
        for client in self.__clientsByConnId.values():
            client.send(data)

    def disconnectAll(self, disconnectReason):
        for client in self.__clientsByConnId.values():
            client.disconnect()

    def clientTick(self):
        # startTimeInMs: Final = curTimeUtc() * 1000
        curTimeUtcInSec = curTimeUtc()
        try:
            if len(self.__clientsByClientId) != 0:
                self.__aiFacade.update()
                for client in self.__clientsByClientId.values():
                    self.__aiFacade.send(client)
                    client.tick(curTimeUtcInSec)

        except Exception as error:
            glog.error("{}: {} - Client tick error, traceback:{}".format(
                type(error).__name__, error, traceback.format_exc()))

    def onSocketClose(self, connId: int):
        client: Final = self.__clientsByConnId[connId]
        if client == None:
            glog.warn("Client not found by connId: {}".format(connId))
            return

        client.onSocketClose()

        self.__removeClient(connId)
        self.__addReservedConnId(connId)
