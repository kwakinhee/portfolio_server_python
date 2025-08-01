from typing import Any, Dict, List
from twisted.web.http import Request
from commonlib.glog import glog
from commonlib.gconf import gconf
from commonlib.gerror import GError
from commonlib.netlib.http.server.json_resource import JsonResource
from commonlib.netlib.http.server.response import JsonResponse, GErrorResponse
from commonlib.util.genum import GERROR_CODE


class Fetch(JsonResource):

    isLeaf = True

    def post(self, request: Request):
        glog.info(f"/fetch {request.body}")

        try:
            # self.__validateParams(request.body)
            from server import ConfigService
            configService = ConfigService()
            config_data: Dict[str, Any] = configService.configData

            path_token_str = request.body.get("configPath", "")
            path_tokens = path_token_str.split("/")

            return_config = config_data

            for path_token in path_tokens:
                if len(path_token) > 0:
                    return_config = return_config.get(path_token)
                    if return_config is None:
                        raise GError(f"Invalid configPath token: [{path_token}]", GERROR_CODE.INVALID_PATH_TOKEN)

        except GError as err:
            return GErrorResponse(err)

        return JsonResponse(return_config)

    # Not used
    # def __validateParams(self, request: Request):
    #     if False:
    #         raise GError(f"Invalid params {request.body}", GERROR_CODE.INVALID_PARAMETER)