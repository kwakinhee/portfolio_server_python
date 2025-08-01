from typing import *
from commonlib.glog import glog
from proto import packet_pb2 as protobuffer
from twisted.internet import reactor
from time import sleep


def pong(botclient, response: protobuffer.Response):
    glog.info("[Bot] response pong: {}".format(response.type))

    def sendPong():
        request = protobuffer.Request()
        request.type = protobuffer.PacketType.PING
        request.cs_ping.serverTimeUtcRequest = True
        botclient.sendProtobufPacket(request)
    
    reactor.callLater(2, sendPong)
