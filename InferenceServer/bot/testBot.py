from bot.botUdpClient import BotUDPClient
from typing import *
from twisted.internet.protocol import Protocol
from struct import pack, unpack
from datetime import datetime
from proto import packet_pb2 as protobuffer
import traceback
import bot.packetHandler.packetHandler as packetHandler


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
class BotTCPClient(Protocol):
    def __init__(self, factory):
        self.factory: Any = factory
        # 서버에서 수신된 버퍼.
        self.__recvBuf: bytearray = bytearray()
        self.__bytesReceived: int = 0
        self.udp = None

    # 클라이언트 세션이 서버 접속 성공 콜백

    def initUDPClient(self, connect_ip, connect_port):
        self.udp = BotUDPClient(connect_host=connect_ip,
                                connect_port=connect_port)
        self.udp.registerHeartbeat()

    def connectionMade(self):

        # 레이턴시 테스트를 위한 변수 선언
        self.prevTime: datetime = datetime.now()
        self.latencyTime: int = 0

        # tcp 서버 접속 여부 설정
        self.tcp_connected: bool = True
        print('[Bot] new client connection')

        request = protobuffer.Request()
        request.type = protobuffer.PacketType.LOGIN
        request.cq_login.clientToken = 'ai01'
        self.sendProtobufPacket(request)

    # 접속이 끊어진 경우 콜백
    def connectionLost(self, reason):
        print('[Bot] connectionLost lost {}'.format(reason.getErrorMessage()))

    # 패킷 전송을 받았을 경우 콜백
    def dataReceived(self, readData):
        print('[Bot] dataReceived')
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

    # 서버로 패킷 전송
    def send(self, buff):
        self.transport.write(buff)

        #레이턴시 테스트를 위해 패킷을 던진 시간 저장
        # self._prevTime = datetime.now()

    def sendProtobufPacket(self,
                           packetBody: protobuffer.Request,
                           payloadFlags: int = None):
        try:
            sendBuf = bytearray()

            body = packetBody.SerializeToString()
            packetSize = len(body)
            sendBuf = pack('iH', packetSize, 1)
            sendBuf += body

            print(
                "[Bot] send packet size: {}, packetType: {}, sendBufLength: {}"
                .format(packetSize, packetBody.type, len(sendBuf)))

            self.transport.write(bytes(sendBuf))
        except Exception as error:
            print("[Bot] {}: {} - Failed to write packet buffer, traceback:{}".
                  format(type(error).__name__, error, traceback.format_exc()))

    # 커넥션 종료
    def close(self):
        self.tcp_connected = False
        self.transport.loseConnection()

    # 커넥팅 시작
    def startedConnecting(self, connector):
        print('[Bot] started connecting..')