from proto import packet_pb2 as protobuf
from commonlib.util.gutil import curTimeUtc

def hello_udp(session, request):
    print(f"[UDP Host] {request.payload}")
    session.last_heartbeat_time = curTimeUtc()
    
def hello_broadcast(session, request):
    # print(f"[BOT][UDP] {request.payload}")
    pass
