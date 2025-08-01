# from twisted.internet import defer
# from twisted.internet.defer import Deferred, returnValue
# from commonlib.netlib.http.client.twistedClient import Client as AsyncClient
import json5
from commonlib.netlib.http.client.requestsClient import Client as SyncClient
from commonlib.gconf import Configuration, gconf

class ConfigApiClientSync(SyncClient):
    def __init__(self, base_url=None, **kwargs):
        super().__init__(base_url=base_url)

    def fetch_config(self):
        response = self.post("fetch", json={"configPath": ""})
        response.raise_for_status()
        full_config = json5.loads(response.content)
        print(full_config)
        # configServer로부터 받은 설정 merge
        gconf.mergeFromServiceGroupConfig(full_config,
                                         f"{gconf.processName}/common")

        gconf.mergeFromServiceGroupConfig(
             full_config, f"{gconf.processName}/instances/{gconf.appId}")

        gconf.serviceGroup = Configuration.convertDictAttributes(
            gconf.serviceGroup)

# Not used
# class ConfigApiClientAsync(AsyncClient):
#     def __init__(self, base_url=None, **kwargs):
#         super().__init__(base_url=base_url)

#     @defer.inlineCallbacks
#     def fetch_config(self) -> Deferred:
#         try:
#             response = yield self.post("fetch", json={"configPath": ""})
#             if response.original.code != 200:
#                 raise Exception("[ {} ] fetch config failed".format(response.original.code))
#             full_config = yield response.json()
#             return full_config
#         except Exception as exc:
#             raise exc
