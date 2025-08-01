from commonlib.netlib.udp.udpProtocol import BaseUDP
from twisted.internet.task import LoopingCall
from commonlib.netlib.udp.udpClientConnection import UDPClientConnFactory
import json
from twisted.internet import reactor


class ServerUDPClient(BaseUDP):
    # message_obj = protobuffer.Request
    def __init__(self, conn_factory=UDPClientConnFactory, message_obj=json.loads, connect_host=None, connect_port=None, listen_port=None):
        super().__init__(conn_factory, message_obj, connect_host, connect_port, listen_port)

        # TODO 나중에 빼야함. 서버 -> 클라 브로드캐스트 테스트
        self.broadcast: LoopingCall = None
        self.broadcast_count = 0
        self.registerBroadcast()

    def broadcastDatagram(self, data):
        if self.connections:
            for connection in self.connections.values():
                connection.send_packet(data)


    def broadcastTest(self):
        data = {
            "type": 2345,
            "payload": f"BroadCast {self.broadcast_count}"
        }
        broadcast = json.dumps(data).encode("utf-8")
        self.broadcastDatagram(broadcast)
        self.broadcast_count += 1


    def registerBroadcast(self):
        self.broadcast = LoopingCall(self.broadcastTest)
        reactor.callLater(3, self.broadcast.start, 0, False)


    def stopProtocol(self):
        print(f"transport is closed")
        if self.broadcast and self.broadcast.running:
            self.broadcast.stop()
