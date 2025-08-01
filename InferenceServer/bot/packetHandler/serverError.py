from typing import *
from commonlib.glog import glog
from proto import packet_pb2 as protobuffer


def serverError(botclient, response: protobuffer.Response):
    glog.info(
        "[Bot] response serverError packetType: {}, errCode: {}, errMessage:{}"
        .format(response.type, response.server_error.errCode,
                response.server_error.errMessage))
