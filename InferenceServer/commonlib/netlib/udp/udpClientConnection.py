from collections import deque, namedtuple
from twisted.internet.task import LoopingCall
from aiServer.packetHandler.udp import udpPacketHandler
from enum import Enum
from commonlib.util.gutil import curTimeUtc


class State(Enum):
    CONNECTED = 0
    SHUTDOWN = 1

class UDPClientConnection(object):

    _Address = namedtuple('Address', ['ip', 'port'])
    HEARTBEAT_INTERVAL = 7

    def __init__(self, protocol, host_addr, remote_addr):
        self.__protocol = protocol
        self.host_addr = self._Address(*host_addr)
        self.remote_addr = self._Address(*remote_addr)
        self.__recv_queue = deque()
        self.recv_loop = LoopingCall(self.__pop_inbound_packet)
        self.state = State.CONNECTED

        self.last_heartbeat_time = curTimeUtc()
        self.health_check = LoopingCall(self.check_health)
        self.health_check.start(self.HEARTBEAT_INTERVAL, True)

    def __push_recv_packet(self, udpPacket):
        self.__recv_queue.append(udpPacket)


    def __pop_recv_packet(self):
        return self.__recv_queue.popleft()


    def check_health(self):
        currTime = curTimeUtc()
        if currTime - self.last_heartbeat_time > self.HEARTBEAT_INTERVAL:
            print(f"[UDP][HOST] heatbeat timeout. shutdown client [ {self.remote_addr} ]")
            self.shutdown()
            self.unregister()

    # Packet Receive Logic
    def receive_packet(self, udpPacket, addr):
        # pre-process packet into PacketType here
        if self.state == State.SHUTDOWN:
            return
        self.__process_packet(udpPacket)


    def __process_packet(self, udpPacket):
        self.__push_recv_packet(udpPacket)
        self.__start_recv_loop()


    def __pop_inbound_packet(self):
        packet = self.__pop_recv_packet()

        if packet is None:
            self.__stop_recv_loop()
        else:
            udpPacketHandler.exec(self, packet)

            if not self.__recv_queue:
                self.__stop_recv_loop()


    # Receive Loop 
    def __start_recv_loop(self):
        if not self.recv_loop.running and self.__recv_queue:
            self.recv_loop.start(0, now=True)


    def __stop_recv_loop(self):
        if self.recv_loop.running:
            self.recv_loop.stop()


    def send_packet(self, data):
        # protobuf 교체 + validation
        self.__protocol.sendDatagram(data, self.remote_addr)


    def shutdown(self):
        self.state = State.SHUTDOWN
        self.__stop_recv_loop()
        self.health_check.stop()


    def unregister(self):
        del self.__protocol.connections[tuple(self.remote_addr)]


class UDPClientConnFactory(object):
    def make_new_connection(protocol, host_addr, remote_addr):
        new_connection = UDPClientConnection(protocol, host_addr, remote_addr)
        return new_connection
