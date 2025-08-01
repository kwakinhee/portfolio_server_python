from typing import Dict, List
from collections import namedtuple
from google.protobuf.message import DecodeError
from proto import packet_pb2 as protobuffer
from twisted.internet.protocol import DatagramProtocol
from twisted.internet.task import LoopingCall
from commonlib.netlib.udp.udpClientConnection import UDPClientConnection, UDPClientConnFactory
import json
from twisted.internet import reactor


class ValidationError(Exception):
    pass

class Packet:
    def __init__(self, type, payload):
        self.type = type
        self.payload = payload

    def validate(self):
        if not self.type:
            raise ValidationError("Invalid Packet!")


class BaseUDP(DatagramProtocol):

    def __init__(self, conn_factory=UDPClientConnFactory, message_obj=json.loads, connect_host=None, connect_port=None, listen_port=None):
        self.conn_factory = conn_factory
        self.host = None
        self.port = None
        self.listen_port = listen_port
        self.connect_host = connect_host
        self.connect_port = connect_port
        self.message_obj = message_obj
        self.connections: Dict[namedtuple, UDPClientConnection] = {}
        self.max_connection_count = 1

    def isAvailable(self):
        return len(self.connections) < self.max_connection_count

    def isEmpty(self):
        return len(self.connections) == 0

    def startProtocol(self):
        self.host = self.transport.getHost().host
        self.port = self.transport.getHost().port
        print(f"Udp Init {self.host}:{self.port}")

    def datagramReceived(self, datagram: str, remote_addr):
        try:
            recv_data = self.message_obj(datagram)
            packet = Packet(**recv_data)
            packet.validate()

            # PROTOBUF
            # request = protobuffer.Request()
            # request.ParseFromString(datagram)
            # validate(request)

        except (DecodeError, TypeError, ValueError) as exc:
            print(f"[DatagramReceived]: {exc.__class__.__name__}. {datagram}")

        except ValidationError as exc:
            print(f"[DatagramReceived]: {exc.__class__.__name__}. {datagram}")

        else:
            connection = self.connections.get(remote_addr, None)
            if connection is None:
                connection = self.makeNewConnection(
                    (self.host, self.port),
                    remote_addr,
                )
            if connection is not None:
                connection.receive_packet(packet, remote_addr)


    def makeNewConnection(self, host_addr, remote_addr):
        connection = self.conn_factory.make_new_connection(
            self,
            host_addr,
            remote_addr,
        )
        self.connections[remote_addr] = connection
        return connection


    def sendDatagram(self, data, addr):
        self.transport.write(data, addr)


    def listen(self):
        print(f"[UDP] init server UDP at {self.listen_port}")
        port = self.listen_port if self.listen_port is not None else 0
        reactor.listenUDP(port, self)

    
    def shutdown(self):
        for key, session in self.connections.items():
            session.shutdown()
            del self.connections[key]