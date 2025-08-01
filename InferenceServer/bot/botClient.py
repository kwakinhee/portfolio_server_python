from typing import *
from twisted.internet.protocol import Protocol
from struct import pack, unpack
from datetime import datetime
from datetime import timedelta
from proto import packet_pb2 as protobuffer
from commonlib.glog import glog
import traceback
import bot.packetHandler.packetHandler as packetHandler


# Decorator
def constant(func):
    def func_set(self, value):
        raise TypeError

    def func_get(self):
        return func()

    return property(func_get, func_set)


class _Packet_size_info:
    @constant
    def HEADER_LEN():
        return 6  # packtBodySize 4byte , flags 2byte


PACKET_SIZE_INFO = _Packet_size_info()


# 서버로 접속한 클라이언트 세션 프로토콜
class BotClient(Protocol):
    def __init__(self, factory):
        self.factory: Any = factory

        # 서버에서 수신된 버퍼.
        self.__recvBuf: bytearray = bytearray()
        self.__bytesReceived: int = 0

    # 클라이언트 세션이 서버 접속 성공 콜백
    def connectionMade(self):

        # 레이턴시 테스트를 위한 변수 선언
        self.prevTime: datetime = datetime.now()
        self.latencyTime: int = 0

        # tcp 서버 접속 여부 설정
        self.tcp_connected: bool = True
        glog.info('[Bot] new client connection')

        request = protobuffer.Request()
        request.type = protobuffer.PacketType.LOGIN
        request.cq_login.clientToken = 'ai01'
        self.sendProtobufPacket(request)

    # 접속이 끊어진 경우 콜백
    def connectionLost(self, reason):
        glog.info('[Bot] connectionLost lost {}'.format(
            reason.getErrorMessage()))

    # 패킷 전송을 받았을 경우 콜백
    def dataReceived(self, readData):
        glog.info('[Bot] dataReceived')
        self.__recvBuf += readData
        self.__bytesReceived += len(readData)

        while True:
            if self.__bytesReceived < PACKET_SIZE_INFO.HEADER_LEN:
                break

            # packetHeader read
            packetbodySize: int = int.from_bytes(self.__recvBuf[0:4], 'big')
            payloadflags: int = int.from_bytes(self.__recvBuf[4:6], 'big')

            numBytesToDiscard: int = PACKET_SIZE_INFO.HEADER_LEN + packetbodySize
            if self.__bytesReceived < numBytesToDiscard:
                break

            numBytesRemaining: Final = self.__bytesReceived - numBytesToDiscard
            self.__bytesReceived = numBytesRemaining

            # 헤더사이즈를 제외한 실제 bodySize 만큼 추출.
            packetBuff: bytearray = self.__recvBuf[
                PACKET_SIZE_INFO.HEADER_LEN:numBytesToDiscard]
            self.__recvBuf = self.__recvBuf[numBytesToDiscard:]

            response = protobuffer.Response()
            response.ParseFromString(packetBuff)

            packetHandler.exec(self, response)

        # self.buf += data
        # while True:
        #     if len(self.buf) >= 4:
        #         (length, seq) = unpack("iH", self.buf[0:4])
        #         if length == 0:
        #             print "length 0 error"
        #             self.buf = self.buf[4:]
        #             continue

        #         if length > 1024:
        #             print "error - big length %d" % length
        #             self.transport.loseConnection()
        #             break

        #         if length > 0 and len(self.buf) >= length + 4:
        #             packet = self.buf[4:length + 4]
        #             self.buf = self.buf[length + 4:]
        #             response = protobuffer.Response()
        #             response.ParseFromString(packet)
        #             self.handleResponse(response)
        #             continue
        #     else:
        #         break

    # 서버로 패킷 전송
    def send(self, buff):
        # buff.sequence = self.seq_cnt
        # self.seq_cnt += 1
        # body = buff.SerializeToString()
        # data = pack('HH', len(body), 1)
        # data += body
        self.transport.write(buff)

        #레이턴시 테스트를 위해 패킷을 던진 시간 저장
        self._prevTime = datetime.now()

    def sendProtobufPacket(self,
                           packetBody: protobuffer.Request,
                           payloadFlags: int = None):
        try:
            sendBuf = bytearray()
            # packetHeader: PacketHeader = PacketHeader()
            # packetHeader.setPacketId(packetBody.getPacketId())
            # packetHeader.setPacketBodySize(packetBody.getPacketBodySize())
            # packetHeader.serialize(sendBuf)
            # packetBody.serialize(sendBuf)

            body = packetBody.SerializeToString()
            packetSize = len(body)
            sendBuf = pack('iH', packetSize, 1)
            sendBuf += body

            glog.info("[Bot] send packet size: {}, packetType: {}".format(
                packetSize, packetBody.type))

            self.transport.write(bytes(sendBuf))
        except Exception as error:
            glog.warn(
                "[Bot] {}: {} - Failed to write packet buffer, traceback:{}".
                format(type(error).__name__, error, traceback.format_exc()))

    # 커넥션 종료
    def close(self):
        self.tcp_connected = False
        self.transport.loseConnection()

    # 커넥팅 시작
    def startedConnecting(self, connector):
        glog.info('[Bot] started connecting..')
