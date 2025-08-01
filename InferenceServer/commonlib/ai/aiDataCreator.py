from commonlib.ai.model import Model
from commonlib.gconf import ModelData
from commonlib.gconf import DataInfos
from commonlib.ai.aiNode import AINode
from typing import *


# AI data creator
class AiDataCreator:
    def __init__(self):
        pass

    # aiFacade 에서 생성.
    @staticmethod
    def createModel(modelData: ModelData):
        return Model(modelData)

    @staticmethod
    def createAINode(modelData: ModelData, dataInfos: DataInfos):
        model: Model = AiDataCreator.createModel(modelData)
        return AINode(model, dataInfos)

    # fileLoader 에서 생성.
    @staticmethod
    def createModelData(root: str, modelInfo: object):
        return ModelData(root, modelInfo)

    @staticmethod
    def createDataInfos(root: str, dataInfo: object):
        return DataInfos(root, dataInfo)

    @staticmethod
    def createPcaData(positionType: str, dirPath: str, fileName: str):
        from commonlib.gconf import PcaData
        return PcaData(positionType, dirPath, fileName)

    @staticmethod
    def createInputData(dirPath: str, dataType: int, metaData: object):
        from commonlib.gconf import InputData
        return InputData(dirPath, dataType, metaData)
