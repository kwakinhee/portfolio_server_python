from typing import *
from twisted.internet.protocol import Protocol
from struct import pack, unpack
from commonlib.gconf import gconf
from commonlib.util.gutil import curTimeUtc
from commonlib.gerror import GError
from datetime import timedelta
from clientConnection import ClientConnection, DISCONNECT_REASON, Payload, CONNECTION_STATE
import numpy
from proto import packet_pb2 as protobuffer
from commonlib.glog import glog
from commonlib.util.genum import PAYLOAD_FLAG, GERROR_CODE
import asyncio
import aiServer.packetHandler.packetHandler as packetHandler
import traceback
from dataclasses import dataclass
from pyee import EventEmitter
from contextlib import suppress
from twisted.internet import reactor, defer

from clientMgr import ClientMgr


# todo 추후 DB 에서 정보를 가져옴.
@dataclass()
class LoginInfo:
    clientId: int
    clientToken: str


# 서버로 접속한 서버상의 클라이언트 세션 프로토콜
class Client(Protocol):
    # ServerFactory 에서 생성.
    def __init__(self, gServerfactory):
        self.factory = gServerfactory

        # client seesion 관리.
        self.__clientMgr: ClientMgr = ClientMgr()

        # 핑 테스트를 위한 변수 선언.
        self.__lastPingTimeUtcInSec: int = curTimeUtc()
        self.__lastPingPongTickTimeUtcInSec: int = 0

        # session별 connection 기능.
        self.__clientConn: ClientConnection = None
        self.__disconnectReason: DISCONNECT_REASON = None

        # 서버 접속시 서버에서 생성되는 connId.
        self.__connId: int = 0

        # 로그인시 서버에서 생성하는 id.
        self.__clientId: int = 0

        # 로그인시 언리얼 클라이언트에서 생성하는 token.
        self.__clientToken: str = ""

        # 로그아웃을 기다리기 위한 이벤트 오브젝트.
        self.__logoutEvent: EventEmitter = None
        self.__loginDefer: defer.Deferred = None
        self.__blogout: bool = False

    def getConnId(self):
        return self.__connId

    def getClientId(self):
        return self.__clientId

    def getClientToken(self):
        return self.__clientToken

    def getConnState(self):
        return self.__clientConn.connectionState

    def _setConnState(self, connectionState: CONNECTION_STATE):
        self.__clientConn.connectionState = connectionState

    def login(self, loginInfo: LoginInfo):
        self._setConnState(CONNECTION_STATE.LOGGED_IN)

        self.__clientId = loginInfo.clientId
        self.__clientToken = loginInfo.clientToken

        self.__clientMgr.addLoggedInClient(self)

        response = protobuffer.Response()
        response.type = protobuffer.PacketType.LOGIN
        response.sa_login.result = True
        self.send(response)

        glog.info("client login , clientId: {} cliteToken: {} ".format(
            self.__clientId, self.__clientToken))

    def logout(self):
        currentConnState = self.getConnState()
        if currentConnState == CONNECTION_STATE.LOGGED_OUT:
            glog.warn(
                "client logout when already logged out , clientId: {} connState: {} "
                .format(self.__clientId, self.getConnState()))
            return

        # 아직 로그인이 안된 클라이언트.
        if currentConnState == CONNECTION_STATE.JUST_CONNECTED:
            return

        self._setConnState(CONNECTION_STATE.LOGGED_OUT)
        self.__clientMgr.removeLoggedInClient(self.__clientId,
                                              self.__clientToken)

        glog.info(
            "client logout, clientId: {} connId: {}  disconnectReason: {}".
            format(self.__clientId, self.getConnState(),
                   self.__disconnectReason))

        if self.__logoutEvent:
            self.__logoutEvent.emit("logout")

    # 기존 유저 logout 비동기 wait.
    def waitForLogout(self, clientLoginFunc, loginInfo: LoginInfo):
        self.__logoutEvent = EventEmitter()

        self.__loginDefer = defer.Deferred()
        self.__loginDefer.addCallback(clientLoginFunc)

        @self.__logoutEvent.on('logout')
        def logoutSuccess():
            if self.__blogout == False:
                self.__blogout = True
                self.__loginDefer.callback(loginInfo)
            else:
                glog.warn("already logout Success")

        def checkTimeOut():
            if self.__blogout == False:
                self.__blogout = True
                self.__loginDefer.callback(loginInfo)

        reactor.callLater(3, checkTimeOut)

    # event driven func ---------------------------------------------------------------

    # 클라이언트 세션이 서버 접속 성공 콜백
    def connectionMade(self):

        # session connection 관련 기능 클래스 정의.
        self.__clientConn: ClientConnection = ClientConnection(self.transport)

        # 서버로 접속한 클라이언트 커넥션 번호
        self.__connId: int = self.__clientMgr.popReservedConnId()
        self.__clientMgr.addClient(self.__connId, self)

        glog.info("[SOCKET] new client connection, connId: {}".format(
            self.__connId))

    # 접속이 끊어진 경우 콜백
    def connectionLost(self, reason):

        self.__clientMgr.onSocketClose(self.__connId)

        glog.info("[SOCKET] connection lost, connId: {}, reason:{}".format(
            self.__connId, reason))

    # 패킷 전송을 받았을 경우 콜백
    def dataReceived(self, readData):
        try:
            glog.info(
                "[SOCKET] received from client, connId: {}, readByteLen {}".
                format(self.__connId, len(readData)))

            payloads: List[Payload] = self.__clientConn.receivePayloads(
                readData)

            if len(payloads) == 0:
                return

            # todo 패킷량이 점점 부하가 많아질 경우 처리.
            payloadQueuedSize: int = self.__clientConn.getPayloadQueued()
            maxPayloadQueueSize: int = gconf.serviceGroup.maxPayloadQueueSize
            if payloadQueuedSize > maxPayloadQueueSize:
                glog.error(
                    "[SOCKET] payloadSize has been exceeded, self.__clientId:{}, connId: {}, payloadQueuedSize: {}, maxPayloadQueueSize: {}"
                    .format(self.__clientId, self.__connId, payloadQueuedSize,
                            maxPayloadQueueSize))

                self.disconnect(DISCONNECT_REASON.EXCEEDED_PAYLOAD)

            self.__clientConn.enqueuePayloads(payloads)

            if payloadQueuedSize == 0:
                self._tryPayload()

        except Exception as error:
            glog.error(
                "{}: {} - failed to dataReceived  connId:{}, packetLen:{}, traceback:{}"
                .format(
                    type(error).__name__, error, self.__connId, len(readData),
                    traceback.format_exc()))

            self.disconnect(DISCONNECT_REASON.ON_RECV_ERROR)

    # 커넥팅 시작
    def startedConnecting(self, connector):
        glog.debug("[SOCKET] started connecting..")

    # ------------------------------------------------------------------------------------
    # payload 처리.
    def _tryPayload(self):
        peekPayload: Payload = self.__clientConn.peekPayload()

        if peekPayload == None:
            return

        # todo 로그아웃 payload 특별 처리.
        if peekPayload.flags == PAYLOAD_FLAG.LOGOUT.value[0]:
            self.logout()
            return

        if self.__disconnectReason:
            # 연결이 끊긴 상태이면, 일반 패킷 처리는 스킵.
            self.__clientConn.dequeuePayload()
            self._tryPayload()
            return

        # async process read payload.
        reactor.callLater(0, self._processPayload, peekPayload)

    # 패킷 방식 변환.
    def _parsePacket(self, payload: Payload):
        # packet: IPacket = PacketFactory().Create(payload.packetId)
        # packet.deserialize(payload.buffer)

        request = protobuffer.Request()
        request.ParseFromString(payload.buffer)
        return request

    def _processPayload(self, payload: Payload):
        packet: protobuffer.Request = None
        try:
            packet = self._parsePacket(payload)

            glog.info(
                "packet received connId:{}, clientId:{}, type:{}, size:{}".
                format(self.__connId, self.__clientId, packet.type,
                       len(payload.buffer)))

            packetHandler.exec(self, packet)

            self.__clientConn.dequeuePayload()
            self._tryPayload()

        except Exception as err:
            try:
                glog.error(
                    "{}: {} - packet processed with error connId:{}, clientId:{}, errCode:{}, errorMessgae:{}, extra:{}, traceback:{}"
                    .format(
                        type(err).__name__, err, self.__connId,
                        self.__clientId,
                        err.gcode if hasattr(err, 'gcode') else None,
                        err.message if hasattr(err, 'message') else None,
                        err.extra if hasattr(err, 'extra') else None,
                        traceback.format_exc()))

                # error 가 custonError 가 아닌경우
                if not isinstance(err, GError):
                    self.__clientConn.sendGError(
                        self.__connId, self.__clientId,
                        GError("{}: {}".format(type(err).__name__, err),
                               GERROR_CODE.INTERNAL_ERROR, None))

                elif isinstance(err, GError) and (
                        gconf.isDev or
                        err.gcode >= GERROR_CODE.NON_FATAL_ERROR_MARK.value):
                    self.__clientConn.sendGError(self.__connId,
                                                 self.__clientId, err)

                self.disconnect(DISCONNECT_REASON.ERROR_OCCURRED)
            except Exception as err:
                print("{}: {} - exception again  traceback:{}".format(
                    type(err).__name__, err, traceback.format_exc()))

                self.disconnect(DISCONNECT_REASON.ERROR_OCCURRED)

    # 클라이언트로 패킷 전송.
    def send(self, response: protobuffer.Response, payloadFlags: int = 0):

        # async send
        # reactor.callLater(0, self.__clientConn.sendProtobufPacket,
        #                   self.__connId, response, payloadFlags)

        self.__clientConn.sendProtobufPacket(self.__connId, self.__clientId,
                                             response, payloadFlags)

    # 커넥션 종료
    def disconnect(self, disconnectReason: DISCONNECT_REASON):
        glog.info(
            "Disconnecting client connId:{}, disconnectReason: {}".format(
                self.__connId, disconnectReason))

        if self.__disconnectReason:
            glog.warn(
                "Trying to set disconnect reason more than once connId:{}, old disconnectReason:{}, new disconnectReason:{}"
                .format(self.__connId, self.__disconnectReason,
                        disconnectReason))
        else:
            self.__disconnectReason = disconnectReason

        self.__clientConn.disconnect()

    def onSocketClose(self):
        if self.__disconnectReason == None:
            self.__disconnectReason = DISCONNECT_REASON.SOCKET_CLOSED

        # todo payload logout 처리 추가 예정.
        payloadQueuedSize: int = self.__clientConn.getPayloadQueued()
        logoutPayload = Payload(PAYLOAD_FLAG.LOGOUT.value[0], None)
        self.__clientConn.enqueuePayloads([logoutPayload])

        if payloadQueuedSize == 0:
            self._tryPayload()

    # 클라이언트 세션마다 tick update
    def tick(self, curTimeUtcInSec):
        if self.getConnState() != CONNECTION_STATE.LOGGED_IN:
            return

        self.pingpongTick(curTimeUtcInSec)

    def pingpongTick(self, curTimeUtcInSec: int):
        # todo ping 값 설정으로 빼야함.
        pingPongIntervalSec = gconf.serviceGroup.clientTick.pingPongIntervalSec
        if curTimeUtcInSec - self.__lastPingPongTickTimeUtcInSec < pingPongIntervalSec:
            return

        self.__lastPingPongTickTimeUtcInSec = curTimeUtcInSec
        timeout = gconf.serviceGroup.ping.timeout
        elapsedSecs: final = curTimeUtcInSec - self.__lastPingTimeUtcInSec

        if elapsedSecs * 1000 <= timeout:
            return

        glog.warn("ping timeout, clientId: {}, elapsedSecs: {}".format(
            self.__clientId, elapsedSecs))

        self.disconnect(DISCONNECT_REASON.PING_TIMEOUT)

    def updateLastPingTime(self):
        self.__lastPingTimeUtcInSec = curTimeUtc()
