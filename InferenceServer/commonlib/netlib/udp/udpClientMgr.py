from twisted.internet.task import LoopingCall
from commonlib.util.singleton import Singleton
from aiServer.udpClient import ServerUDPClient

class UDPClientManager(metaclass=Singleton):
    
    clients = []
    clientFactory = ServerUDPClient
    def __init__(self):
        self.__cleanUp = LoopingCall(self.cleanUDPClients)
        self.__cleanUp.start(10, False)


    def createUDPClient(self, **kwargs):
        new_client = self.clientFactory(**kwargs)
        new_client.listen()
        self.clients.append(new_client)
        return new_client


    def cleanUDPClients(self):
        if not self.clients:
            return

        for client in self.clients[:]:
            if client.isEmpty():
                self.clients.remove(client)
                

    def getUDPClient(self): 
        for client in self.clients: 
            if client.isAvailable():
                return client
        return None
    

    def getOrCreateUdpClient(self):
        client = self.getUDPClient()
        if not client:
            client = self.createUDPClient()
        return client
