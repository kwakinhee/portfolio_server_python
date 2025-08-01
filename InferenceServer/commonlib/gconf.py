from typing import *
import os
import platform
from commonlib.configLoader import loadConfig

class Dict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


# class List(list):
#     """dot.notation access to list attributes"""
#     __getattr__ = list.__getattribute__
#     __setattr__ = list.__setitem__
#     __delattr__ = list.__delitem__


class Configuration(object):
    @staticmethod
    def __load__(data):
        if type(data) is dict:
            return Configuration.convertDictAttributes(data)
        elif type(data) is list:
            return Configuration.convertListAttributes(data)
        else:
            return data

    @staticmethod
    def convertDictAttributes(configDataDic: dict):
        result = Dict()
        for key, value in configDataDic.items():
            result[key] = Configuration.__load__(value)

        return result

    @staticmethod
    def convertListAttributes(configDataList: list):
        result: List[Any] = []
        for value in configDataList:
            result.append(Configuration.__load__(value))

        return result


class ModelData:
    modelName: str
    modelPath: str
    metaData: object

    def __init__(self, root: str, modelInfo: object):
        self.modelName = modelInfo.name
        self.path = os.path.join(root, modelInfo.path)
        self.metaData = modelInfo.metaData


class DataInfos:
    dataInfo: object

    def __init__(self, root: str, dataInfo: object):
        self.dataInfo = self.__load_data_info__(os.path.join(root, dataInfo.path))

    def __load_data_info__(self, path):
        from commonlib.fileLoader import FileLoader

        return FileLoader.loadDataInfo(path)


class InputData:
    dirPath: str
    dataType: int
    metaData: object

    def __init__(self, dirPath: str, dataType: int, metaData: object):
        self.dirPath = dirPath
        self.dataType = dataType
        self.metaData = metaData


# config\default.json5, service_group\dev.json5 설정 관리.
class GConf:
    def __init__(self):

        # 같은 서버끼리의 고유한 id.
        self.appInstanceId = "0" if os.environ.get(
            "APP_INSTANCE_ID") is None else os.environ.get("APP_INSTANCE_ID")

        self.isDev = True if os.environ.get(
            "PYTHON_ENV") != "production" else False

        self.hostname = platform.node()

        self.processName = os.environ.get("PROCESS_TITLE") if os.environ.get(
            "PROCESS_NAME") is None else os.environ.get("PROCESS_NAME")

        # self.appId = f"{self.processName }.{self.appInstanceId}@{self.hostname}"
        # TODO 컨테이너환경에서 hostname이 동적으로 할당되어 임시로 localhost로 수정.
        self.appId = f"{self.processName }.{self.appInstanceId}@localhost"

        # import inspect
        # print(inspect.getmembers(os.environ))

        # config\default.json5 설정.
        self.log: Dict = {}
        self.inputData: InputData = {}
        self.modelDataDic: Dict[str, ModelData] = {}

        self.__loadCommonConfig()

        #  service_group\dev.json5 설정.
        self.serviceGroup: Dict = {}

    def __loadCommonConfig(self):
        configFile = os.environ.get("INFERENCE_CONFIG_FILE_NAME")
        if configFile == None:
            configFile = "default.json5"

        confgidDic: dict = loadConfig("config/", configFile)
        config = Configuration.convertDictAttributes(confgidDic)

        # log
        self.log: dict = config.log

        if self.processName == "configServer":
            return

        # aiData 들을 알맞는 컨테이너로 가공.
        from commonlib.ai.aiDataCreator import AiDataCreator
        aiInfos = config.aiInfos
        self.modelData = AiDataCreator.createModelData(aiInfos.root,
                                                       aiInfos.modelInfo)
        self.dataInfos = AiDataCreator.createDataInfos(aiInfos.root,
                                                       aiInfos.dataInfo)
        aiInputInfos = config.inputData
        self.inputData = AiDataCreator.createInputData(aiInputInfos.dirPath,
                                                       aiInputInfos.dataType,
                                                       aiInputInfos.metaData)

    # todo configServer 에 restApi /fetch 요청후 병합 임시 로직.
    def mergeFromServiceGroupConfig(self, serviceGroupCfg: dict,
                                    configPath: str):
        pathTokens: Final = configPath.split("/")
        tmpCfg: dict = serviceGroupCfg
        for pathToken in pathTokens:
            if len(pathToken) > 0:
                # glog.debug(
                #     f"forEach before pathToken  [{pathToken}]...`, { tmpCfg }")

                tmpCfg = tmpCfg[pathToken]

                # glog.debug(f"forEach after pathTokens ...`, { tmpCfg }")

        self.append(tmpCfg)

    # 현재 서버에 관련된 config 만 병합.
    def append(self, othersConfig: dict):
        # 원본 데이터 수정 조심.
        self.serviceGroup.update(othersConfig)


gconf = GConf()
