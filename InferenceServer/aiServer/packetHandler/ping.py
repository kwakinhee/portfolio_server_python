from proto import packet_pb2 as protobuffer
from typing import *
from commonlib.glog import glog
from commonlib.util.gutil import curTimeUtc
from clientConnection import CONNECTION_STATE
from datetime import datetime, timezone


def ping(client, request: protobuffer.Request):
    glog.info("ping, packetType: {}".format(request.type))
    currentConnState: CONNECTION_STATE = client.getConnState()
    if currentConnState != CONNECTION_STATE.LOGGED_IN:
        glog.warn("ping conn session, clientId: {}, connId: {}, connState: {}".
                  format(client.getClientId(), client.getConnId(),
                         currentConnState))
        return

    client.updateLastPingTime()

    response = protobuffer.Response()
    response.type = protobuffer.PacketType.PONG
    if request.cs_ping.serverTimeUtcRequest:
        response.sc_pong.serverTimeUtc = curTimeUtc()
    client.send(response)
