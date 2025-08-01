from commonlib.netlib.udp.udpProtocol import BaseUDP
from twisted.internet.task import LoopingCall
from commonlib.netlib.udp.udpClientConnection import UDPClientConnFactory
import json
from twisted.internet import reactor


class BotUDPClient(BaseUDP):
    # message_obj = protobuffer.Response
    def __init__(self, session_factory=UDPClientConnFactory, message_obj=json.loads, connect_host=None, connect_port=None, listen_port=None):
        super().__init__(session_factory, message_obj, connect_host, connect_port, listen_port)
        self.heartbeat: LoopingCall = None
        self.connected = False


    def startProtocol(self):
        self.host = self.transport.getHost().host
        self.port = self.transport.getHost().port
        self.transport.connect("10.0.23.51", self.connect_port)
        print(f"Udp Init {self.host}:{self.port}")

    def sendHeartbeat(self):
        data = {
            "type": 1234,
            "payload": f"Heartbeat from {self.host}:{self.port}"
        }
        heartbeat = json.dumps(data).encode("utf-8")
        print(f"[BOT][UDP] heartbeat to: {self.connect_host}:{self.connect_port}")
        self.sendDatagram(data=heartbeat, addr=("10.0.23.51", self.connect_port))


    def registerHeartbeat(self):
        self.connected = True
        print(f"[BOT][UDP] init UDP Client")
        reactor.listenUDP(0, self)
        self.heartbeat = LoopingCall(self.sendHeartbeat)
        self.heartbeat.start(2, now=False)
    
    
    def stopProtocol(self):
        print(f"[BOT][UDP] transport is closed")
        if self.heartbeat and self.heartbeat.running:
            self.heartbeat.stop()