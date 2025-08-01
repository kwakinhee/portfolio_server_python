# import dataclasses
import numpy as np
from abc import *  # Abstrace Base Class
from enum import Enum, unique
import sys, os
from typing import *


# packet abstract class
class IPacket(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def getPacketId(self):
        pass

    @abstractmethod
    def getPacketBodySize(self):
        pass

    @abstractmethod
    def serialize(self, sendBuf: bytearray):
        pass

    @abstractmethod
    def deserialize(self, recvBuf: bytearray):
        pass


# packet Header class
class PacketHeader(IPacket):
    def __init__(self):
        pass

    def setPacketBodySize(self, packetBodySize):
        self.__packetBodySzie: int = packetBodySize

    def getPacketBodySize(self):
        return self.__packetBodySzie

    def serialize(self, sendBuf: bytearray):
        sendBuf += self.__packetBodySzie.to_bytes(4, 'big')

    def deserialize(self, recvBuf: bytearray):
        self.__packetBodySzie = int.from_bytes(recvBuf[0:4], 'big')
        pass


@unique
class PACKET_ID(Enum):
    NONE = 0,
    KEEP_ALIVE = 1,
    # SC_BLENDSHAPE_DATA = 230,
    COORDS = 235,
    # IMAGE = 240,
    # IMAGE_WITH_CLASS_ID = 246,
    # CPT_PACKET = 250,
    TEST = 500,
    CSCONNECT = 320,


class Alive(IPacket):
    def __init__(self):
        pass

    def getPacketId(self):
        return PACKET_ID.KEEP_ALIVE.value[0]

    def getPacketBodySize(self):
        return 0

    def serialize(self, sendBuf: bytearray):
        pass

    def deserialize(self, recvBuf: bytearray):
        pass


# sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
# from commonlib.factory.packetFactory import PacketFactory

# PacketFactory().Register(PACKET_ID.KEEP_ALIVE.value[0], Alive())


class Coords(IPacket):

    COORDS_NUM = 69
    IMG_WIDTH = 384
    IMG_HEIGHT = 288

    #     IMG_WIDTH = 384
    #     IMG_HEIGHT = 288
    #     REGIONS_NUM = 12
    #     COORDS_NUM = 69
    #     UNDEFINE_VALUE = -999.0

    def __init__(self):
        pass

    def getPacketId(self):
        return PACKET_ID.COORDS.value[0]

    def setCoordsInfo(self, coordinates: np.array([]), img: np.array([]),
                      eye_track: np.array([])):
        self.coordinates: np.array([]) = coordinates.astype('float32')
        self.img: np.array([]) = img.astype('uint8')
        self.eye_track: np.array([]) = eye_track.astype('float32')

    def getPacketBodySize(self):
        return 4 * Coords.COORDS_NUM + Coords.IMG_WIDTH * Coords.IMG_HEIGHT + 4 * 4

    def serialize(self, sendBuf: bytearray):
        self.img = np.transpose(self.img)

        sendBuf += bytearray(self.coordinates.reshape(-1))
        sendBuf += bytearray(self.img.reshape(-1))
        sendBuf += bytearray(self.eye_track.reshape(-1))

    def deserialize(self, recvBuf: bytearray):
        pivot = 4
        self.coordinates = np.frombuffer(recvBuf[pivot:],
                                         dtype='float32').reshape(
                                             (1, Coords.COORDS_NUM))
        pivot += 4 * Coords.COORDS_NUM
        self.img = np.frombuffer(recvBuf[pivot:], dtype='uint8').reshape(
            (1, Coords.IMG_WIDTH * Coords.IMG_HEIGHT))
        pivot += Coords.IMG_WIDTH * Coords.IMG_HEIGHT
        self.eye_track = np.frombuffer(recvBuf[pivot:], dtype='float').reshape(
            (2, 2))


# PacketFactory().Register(PACKET_ID.COORDS.value[0], Coords())


class CSConnect(IPacket):
    def __init__(self):
        pass

    def getPacketId(self):
        return PACKET_ID.CSCONNECT.value[0]

    def getPacketBodySize(self):
        return 0

    def serialize(self, sendBuf: bytearray):
        pass

    def deserialize(self, recvBuf: bytearray):
        pass


# PacketFactory().Register(PACKET_ID.CSCONNECT.value[0], CSConnect())


class TEST(IPacket):
    def __init__(self):
        pass

    def getPacketId(self):
        return PACKET_ID.TEST.value[0]

    def setTestInfo(self, sendSequence, startTimeInMs):
        self.__sendSequence = sendSequence
        self.__startTimeInMs = startTimeInMs
        pass

    def getPacketBodySize(self):
        return 4 + 4

    def serialize(self, sendBuf: bytearray):
        sendBuf += self.__sendSequence.to_bytes(4, 'big')
        sendBuf += self.__startTimeInMs.to_bytes(4, 'big')
        pass

    def deserialize(self, recvBuf: bytearray):
        self.__sendSequence = int.from_bytes(recvBuf[4:8], 'big')
        pass


# PacketFactory().Register(PACKET_ID.TEST.value[0], TEST())

# class Image(IPacket):

#     IMG_WIDTH = 384
#     IMG_HEIGHT = 288

#     def __init__(self, im=np.array([])):
#         self.im = im.astype('uint8')
#         pass

#     def serialize(self, sendBuf: bytearray):
#         sendBuf = bytearray()
#         # sendBuf += self.__id__.to_bytes(4, 'big')
#         sendBuf += bytearray(self.im.reshape(-1))

#     def deserialize(self, recvBuf: bytearray):
#         self.im = np.frombuffer(recvBuf[4:], dtype=np.uint8).reshape(
#             (Image.IMG_HEIGHT, Image.IMG_WIDTH))

# PacketFactory().Register(PACKET_ID.IMAGE, Image)

# class SCBlendshapeData(IPacket):
#     def __init__():
#         pass

#     def setBlendshapeData(self,
#                           blendshapes=[],
#                           imageData=np.array([]),
#                           coords=[]):
#         self.__blendshapes = blendshapes
#         self.__imageData = imageData
#         self.__coords = coords

#     # def bytesize(self):
#     #     return 4 + 4 * const.BS_COUNT + const.CAM_WIDTH * const.CAM_HEIGHT + 4 * 3 * const.CP_COUNT

#     def serialize(self, sendBuf: bytearray):
#         # res = bytearray()
#         sendBuf += struct.pack('f' * len(self.__blendshapes),
#                                (self.__blendshapes))
#         sendBuf += bytearray(self.__imageData.reshape(-1))
#         sendBuf += struct.pack('f' * len(self.__coords), (self.__coords))

#         # return sendBuf

#     def deserialize(self, recvBuf: bytearray):
#         pass
#         # pivot = 4
#         # self.blendshapes = [
#         #     float.from_bytes(rawdata[pivot + 4 * x:pivot + 4 * x + 4],
#         #                      'big',
#         #                      signed=True) for x in range(const.BS_COUNT)
#         # ]
#         # pivot += 4 * const.BS_COUNT
#         # self.imageData = np.frombuffer(rawdata[pivot:], dtype='uint8').reshape(
#         #     (const.CAM_WIDTH, const.CAM_HEIGHT))
#         # pivot += const.CAM_WIDTH * const.CAM_HEIGHT
#         # self.coords = [
#         #     float.from_bytes(rawdata[pivot + 4 * x:pivot + 4 * x + 4],
#         #                      'big',
#         #                      signed=True) for x in range(3 * const.CP_COUNT)
#         # ]

# PacketFactory().Register(PACKET_ID.SC_BLENDSHAPE_DATA,
#                                   SCBlendshapeData)

# class CptPacket(Packet):

#     IMG_WIDTH = 384
#     IMG_HEIGHT = 288
#     REGIONS_NUM = 12
#     COORDS_NUM = 69
#     UNDEFINE_VALUE = -999.0

#     def __init__(self,
#                  im=np.zeros((384, 288), dtype=np.uint8),
#                  regions=np.zeros((12, ), dtype=np.int16),
#                  coords=np.full((69, ), UNDEFINE_VALUE, dtype=np.float32)):
#         '''
#         regions: [0:4] -> bottom face rectangle UpLeft, BottomRight
#         '''
#         self.im = im.astype(np.uint8)
#         self.regions = regions.astype(np.int16)
#         self.coords = coords.astype(np.float32)

#     # def bytesize(self):
#     #     '''
#     #     Order: packet id -> regions -> image -> coords
#     #     '''
#     #     return 4 \
#     #         + 1 * CptPacket.IMG_WIDTH * CptPacket.IMG_HEIGHT \
#     #         + 2 * CptPacket.REGIONS_NUM \
#     #         + 4 * CptPacket.COORDS_NUM

#     def get_pack_format(self):
#         return '<{}f'.format(CptPacket.COORDS_NUM)

#     def serialize(self, sendBuf: bytearray):
#         # self.im = self.im.reshape((self.im_shape[1], self.im_shape[0]))
#         # res = bytearray()
#         # sendBuf += self.__id__.to_bytes(4, 'big')
#         sendBuf += bytearray(self.im.reshape(-1))
#         sendBuf += bytearray(self.regions)
#         sendBuf += struct.pack(self.get_pack_format(), *self.coords)

#     def deserialize(self, recvBuf: bytearray):
#         pivot = 4
#         next_pivot = pivot + CptPacket.IMG_WIDTH * CptPacket.IMG_HEIGHT
#         self.im = np.frombuffer(recvBuf[pivot:next_pivot], dtype=np.uint8)
#         self.im = self.im.reshape((CptPacket.IMG_HEIGHT, CptPacket.IMG_WIDTH))

#         pivot = next_pivot
#         next_pivot = pivot + 2 * CptPacket.REGIONS_NUM
#         self.regions = np.frombuffer(recvBuf[pivot:next_pivot], dtype=np.int16)

#         pivot = next_pivot
#         self.coords = struct.unpack(self.get_pack_format(), recvBuf[pivot:])

# PacketFactory().Register(PACKET_ID.CPT_PACKET, SCBlendshapeData)

# class ImageWithClassID(Packet):

#     IMG_WIDTH = 512
#     IMG_HEIGHT = 512
#     CHANNEL = 3

#     def __init__(self, im=np.array([]), class_id=0):
#         self.class_id = class_id
#         self.im = im.astype('uint8')

#     # def bytesize(self):
#     #     return 4 + 4 + ImageWithClassID.IMG_WIDTH * ImageWithClassID.IMG_HEIGHT * ImageWithClassID.CHANNEL

#     def serialize(self, sendBuf: bytearray):
#         sendBuf += self.__id__.to_bytes(4, 'big')
#         sendBuf += self.class_id.to_bytes(4, 'big')
#         sendBuf += bytearray(self.im.reshape(-1))

#     def deserialize(self, recvBuf: bytearray):
#         self.class_id = int.from_bytes(recvBuf[4:8], 'big')
#         self.im = np.frombuffer(recvBuf[8:], dtype=np.uint8).reshape(
#             (ImageWithClassID.IMG_HEIGHT, ImageWithClassID.IMG_WIDTH,
#              ImageWithClassID.CHANNEL))

# PacketFactory().Register(PACKET_ID.IMAGE_WITH_CLASS_ID,
#                                   ImageWithClassID)
