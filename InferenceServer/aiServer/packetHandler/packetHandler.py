from typing import *
from commonlib.glog import glog
import sys, os
from commonlib.gerror import GError
from commonlib.util.genum import GERROR_CODE

sys.path.append(
    os.path.dirname(
        os.path.abspath(
            os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))

from proto import packet_pb2 as protobuffer

from aiServer.packetHandler.ping import ping
from aiServer.packetHandler.login import login
from aiServer.packetHandler.connect_udp import connect_udp

packetHandlerDic: Dict[int, Any] = {
    protobuffer.PacketType.LOGIN: login,
    protobuffer.PacketType.PING: ping,
    protobuffer.PacketType.CONNECT_UDP: connect_udp,
}


def exec(client, request: protobuffer.Request):
    packetType = request.type
    # glog.debug("processing packet ... packetId: {}".format(packetType))

    if not packetType in packetHandlerDic:
        glog.error("unknown packet type clientId:{}, packetType: {}".format(
            client.getClientId(), packetType))
        return
        raise GError("unknown-packet-type, packetType: {}".format(packetType),
                     GERROR_CODE.UNKNOWN_PACKET_TYPE)

    handler: Final = packetHandlerDic[packetType]
    return handler(client, request)
