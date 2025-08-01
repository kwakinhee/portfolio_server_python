from commonlib.util.singleton import Singleton
from proto.protocol import IPacket
from typing import *

from commonlib.glog import glog


class PacketFactory(metaclass=Singleton):
    def __init__(self):
        self.__packetCreatorDic: Dict[int, IPacket] = {}
        pass

    def Register(self, packetId, ctor: IPacket):
        exist: IPacket = self.__packetCreatorDic.get(packetId)
        if exist:
            glog.error(
                "exist packetType in PacketFactory packetId: {} packetName: {}"
                .format(packetId, ctor.__class__.__name__))
        else:
            glog.info(
                "packet factory register packetId: {} packetName: {}".format(
                    packetId, ctor.__class__.__name__))
            self.__packetCreatorDic[packetId] = ctor

    def Create(self, packetId):
        try:
            ctor: IPacket = self.__packetCreatorDic[packetId]
            return ctor
        except:
            glog.error(" Create Packet error")
            return
