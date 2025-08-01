from struct import pack, unpack
from datetime import datetime
from datetime import timedelta
from enum import Enum
from dataclasses import dataclass
from typing import *
from commonlib.glog import glog
from twisted.internet.interfaces import ITransport

from proto import packet_pb2 as protobuffer
from collections import deque
import traceback

from commonlib.gerror import GError


# Decorator
def constant(func):
    def func_set(self, value):
        raise TypeError

    def func_get(self):
        return func()

    return property(func_get, func_set)


# const class
class _Packet_size_info:
    @constant
    def HEADER_LEN():
        return 6  # packtBodySize 4byte , flags 2byte

    @constant
    def RECV_BUFF_SIZE():
        return 16384,  # 16kb


PACKET_SIZE_INFO = _Packet_size_info()


class DISCONNECT_REASON(Enum):
    SOCKET_CLOSED = 1,
    ERROR_OCCURRED = 2,
    PING_TIMEOUT = 3,
    STOP_SERVER = 4,
    EXCEEDED_PAYLOAD = 5,
    ON_RECV_ERROR = 6,
    DUPLICATE_LOGIN_KICK = 7,


class CONNECTION_STATE(Enum):
    JUST_CONNECTED = 1,
    LOGGED_IN = 2,
    LOGGED_OUT = 3,


@dataclass()
class Payload:
    flags: int = None
    buffer: bytearray = None


# 서버로 접속한 서버상의 클라이언트 세션 프로토콜.
class ClientConnection:
    def __init__(self, transport):
        self.__transport: ITransport = transport

        self.connectionState: CONNECTION_STATE = CONNECTION_STATE.JUST_CONNECTED

        # 클라이언트에서 수신된 버퍼.
        self.__recvBuf: bytearray = bytearray()
        self.__bytesReceived: int = 0
        self.__payloadQueue: deque = deque()

    def enqueuePayloads(self, payloads: List[Payload]):
        for payload in payloads:
            self.__payloadQueue.append(payload)

    def dequeuePayload(self):
        elem = self.__payloadQueue.popleft()
        # glog.info(f"at dequeuePayload(): payloadQueue: {self.__payloadQueue}")
        return elem

    def getPayloadQueued(self):
        return self.__payloadQueue.__len__()

    def peekPayload(self):
        if self.getPayloadQueued() == 0:
            return

        return self.__payloadQueue[0]

    def receivePayloads(self, readData):
        payloads: List[Payload] = []

        self.__recvBuf += readData
        self.__bytesReceived += len(readData)

        while True:
            if self.__bytesReceived < PACKET_SIZE_INFO.HEADER_LEN:
                # glog.info(f"self.__bytesReceived: {self.__bytesReceived}")
                break

            # packetHeader: PacketHeader = PacketHeader()
            # packetHeader.deserialize(self.__recvBuf)
            # packetbodySize: int = packetHeader.getPacketBodySize()

            # packetHeader read
            packetbodySize: int = int.from_bytes(self.__recvBuf[0:4], 'big')
            payloadflags: int = int.from_bytes(self.__recvBuf[4:6], 'big')

            # # (length, seq) = unpack("HH", self.__recvBuf[0:4])

            # if packetbodySize > PACKET_SIZE_INFO.RECV_BUFF_SIZE:
            #     glog.error("packetbodySize is big")
            #     self.disconnect()
            #     break

            numBytesToDiscard: int = PACKET_SIZE_INFO.HEADER_LEN + packetbodySize
            if self.__bytesReceived < numBytesToDiscard:
                # glog.info(f"bytesReceived: {self.__bytesReceived}, numBytesToDiscard: {numBytesToDiscard}")
                break

            numBytesRemaining: Final = self.__bytesReceived - numBytesToDiscard
            self.__bytesReceived = numBytesRemaining

            # 헤더사이즈를 제외한 실제 bodySize 만큼 추출.
            packetBuff: bytearray = self.__recvBuf[
                PACKET_SIZE_INFO.HEADER_LEN:numBytesToDiscard]
            self.__recvBuf = self.__recvBuf[numBytesToDiscard:]

            payload: Payload = Payload(payloadflags, packetBuff)

            payloads.append(payload)

            # glog.info("payloads: {}".format(payloads))

        return payloads

    def sendProtobufPacket(self, connId: int, clientId: int,
                           packetBody: protobuffer.Response,
                           payloadFlags: int):
        try:
            sendBuf = bytearray()
            # packetHeader: PacketHeader = PacketHeader()
            # packetHeader.setPacketId(packetBody.getPacketId())
            # packetHeader.setPacketBodySize(packetBody.getPacketBodySize())
            # packetHeader.serialize(sendBuf)
            # packetBody.serialize(sendBuf)

            body = packetBody.SerializeToString()
            packetSize = len(body)

            # packet header
            sendBuf = pack('iH', packetSize, payloadFlags)
            sendBuf += body

            # glog.info("send packet size: {}, packetType: {}".format(
            #     packetSize, packetBody.type))

            self.__transport.write(bytes(sendBuf))
        except Exception as error:
            glog.warn(
                "{}: {} - Failed to write packet buffer connId:{}, clientId:{}, traceback:{}"
                .format(
                    type(error).__name__, error, connId, clientId,
                    traceback.format_exc()))

    def sendGError(self,
                   connId: int,
                   clientId: int,
                   err: GError,
                   payloadFlags: int = 0):

        response = protobuffer.Response()
        response.type = protobuffer.PacketType.SERVER_ERROR
        response.server_error.errCode = err.gcode
        response.server_error.errMessage = err.message

        self.sendProtobufPacket(connId, clientId, response, payloadFlags)

    def disconnect(self):
        self.__transport.loseConnection()
