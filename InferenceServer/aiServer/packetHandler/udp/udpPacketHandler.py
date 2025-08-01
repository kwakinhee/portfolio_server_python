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
from aiServer.packetHandler.udp.udp_test import hello_udp, hello_broadcast

udpPacketHandlerDic: Dict[int, Any] = {
    1234: hello_udp,
    2345: hello_broadcast,
}


def exec(client, request: protobuffer.Request):
    packetType = request.type
    # glog.debug("processing packet ... packetId: {}".format(packetType))

    if not packetType in udpPacketHandlerDic:
        glog.error("unknown packet type clientId:{}, packetType: {}".format(
            client.getClientId(), packetType))
        return
        # raise GError("unknown-packet-type, packetType: {}".format(packetType),
        #              GERROR_CODE.UNKNOWN_PACKET_TYPE)

    handler: Final = udpPacketHandlerDic[packetType]
    return handler(client, request)
