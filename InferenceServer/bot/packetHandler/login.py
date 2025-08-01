from time import sleep
from typing import *
from commonlib.glog import glog
from proto import packet_pb2 as protobuffer


def login(botclient, response: protobuffer.Response):
    glog.info("[Bot] response login packetType: {} result: {}".format(
        response.type, response.sa_login.result))

    request = protobuffer.Request()
    request.type = protobuffer.PacketType.PING
    request.cs_ping.serverTimeUtcRequest = True
    botclient.sendProtobufPacket(request)

    request2 = protobuffer.Request()
    request2.type = protobuffer.PacketType.CONNECT_UDP
    request2.cq_connect_udp.clientToken = "ai01"
    botclient.sendProtobufPacket(request2)