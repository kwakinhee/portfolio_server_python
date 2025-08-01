from commonlib.util.singleton import Singleton

from typing import *
from proto import packet_pb2 as protobuffer

from commonlib.ai.aiNode import AINode
from commonlib.ai.aiDataCreator import AiDataCreator
from commonlib.fileLoader import FileLoader
from commonlib.gconf import gconf
from commonlib.glog import glog

import numpy as np


# ai data, logic 관리
class AiFacade(metaclass=Singleton):
    def __init__(self):

        self.__aiNode: AINode
        self.__inputImageDataIter: Iterator
        self.__responsePredictionData: protobuffer.Response()

    def init(self):
        self.__aiNode = AiDataCreator.createAINode(gconf.modelData,
                                                   gconf.dataInfos)

        self.__inputImageDataIter = FileLoader.loadImagesData()

    def update(self):
        inputImageDataIter = next(self.__inputImageDataIter)
        prediction_elements: list[dict[str, Any]] = self.__aiNode.predict(
            inputImageDataIter)

        response = protobuffer.Response()
        response.type = protobuffer.PacketType.PREDICTION_RESULT
        for prediction_element in prediction_elements:
            expression_element = response.sn_prediction_result.expression.elements.add(
            )
            expression_element.idx = prediction_element["idx"]
            expression_element.controlName = prediction_element["controlName"]
            expression_element.value = prediction_element["value"]

        inputImageDatas = inputImageDataIter.reshape(-1).tobytes()
        response.sn_prediction_result.expression.inputImageDatas = inputImageDatas

        self.__responsePredictionData = response

        # for element in self.__responsePredictionData.sn_prediction_result.expression.elements:
        #     glog.info(
        #         "expression_element, expression_element.idx: {}, controlName:{}, value:{}"
        #         .format(element.idx, element.controlName, element.value))

        # glog.info("inputImageDatas bytes: {}".format(
        #     self.__responsePredictionData.sn_prediction_result.expression.
        #     inputImageDatas))

        # packetBody: Coords = PacketFactory().Create(PACKET_ID.COORDS.value[0])
        # packetBody.setCoordsInfo(transformData[1],
        #                          transformData[0].reshape(-1), et)
        # client.send(packetBody)

    def send(self, client):
        client.send(self.__responsePredictionData)

    # model or image 가 변경된경우 리로드.
    def reload(self):
        pass
