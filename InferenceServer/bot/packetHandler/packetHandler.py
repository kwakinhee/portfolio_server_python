from typing import *
from commonlib.glog import glog
from proto import packet_pb2 as protobuffer

from bot.packetHandler.login import login
from bot.packetHandler.pong import pong
from bot.packetHandler.serverError import serverError
from bot.packetHandler.connect_udp import connect_udp, hello_broadcast

packetHandlerDic: Dict[int, Any] = {
    protobuffer.PacketType.LOGIN: login,
    protobuffer.PacketType.PONG: pong,
    protobuffer.PacketType.SERVER_ERROR: serverError,
    protobuffer.PacketType.CONNECT_UDP: connect_udp,
    2345: hello_broadcast,
}


def exec(botclient, response: protobuffer.Response):
    packetType = response.type
    # glog.debug("[Bot] processing packet ... packetId: {}".format(packetType))

    if not packetType in packetHandlerDic:
        glog.error("[Bot] error - unknown packet type packetType: {}".format(
            packetType))
        raise Exception("[Bot] Unknown packet type")

    handler: Final = packetHandlerDic[packetType]
    return handler(botclient, response)
