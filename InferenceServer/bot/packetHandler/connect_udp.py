from proto import packet_pb2 as protobuffer

def connect_udp(botclient, response: protobuffer.Response):

    ip = response.sa_connect_udp.address.ip
    port = response.sa_connect_udp.address.port

    print(f"[Bot] init UDP connection to {ip}:{port}")
    botclient.initUDPClient(ip, port)

def hello_broadcast(session, request):
    print(f"[BOT][UDP] {request.payload}")