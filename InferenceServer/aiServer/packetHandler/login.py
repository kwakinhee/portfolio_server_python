from typing import *
from commonlib.glog import glog
from proto import packet_pb2 as protobuffer
from clientMgr import ClientMgr
from clientConnection import DISCONNECT_REASON


def login(client, request: protobuffer.Request):

    glog.info("login packetType: {} clientToken: {}".format(
        request.type, request.cq_login.clientToken))

    # 중복 로그인 체크.
    # todo 추후 인증서버에서 DB 에서 정보를 가져와서 중복 체크 해야함.
    clientToken: str = request.cq_login.clientToken
    clientMgr: ClientMgr = ClientMgr()
    clientId: int = clientMgr.getClientIdByClientToken(clientToken)

    from client import LoginInfo
    loginInfo = LoginInfo(clientId, clientToken)

    prevClient = clientMgr.getClientByClientId(clientId)
    if prevClient:
        clientMgr.removeLoggedInClient(clientId, clientToken)
        glog.error(
            "duplicate client login clientId: {} clientToken: {}".format(
                clientId, clientToken))

        prevClient.disconnect(DISCONNECT_REASON.DUPLICATE_LOGIN_KICK)

        # 이전 클라이언트를 킥하고 로그아웃까지 대기.
        prevClient.waitForLogout(client.login, loginInfo)

    else:
        client.login(loginInfo)
