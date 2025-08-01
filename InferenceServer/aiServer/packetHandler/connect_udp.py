from commonlib.netlib.udp.udpClientMgr import UDPClientManager
from proto import packet_pb2 as protobuf

def connect_udp(client, request):
    print("UDP Connect Request from : ", request.cq_connect_udp.clientToken)
    udpClient = UDPClientManager().getOrCreateUdpClient()

    response = protobuf.Response()
    response.type = protobuf.PacketType.CONNECT_UDP
    response.sa_connect_udp.address.ip = udpClient.host
    response.sa_connect_udp.address.port = udpClient.port

    client.send(response)