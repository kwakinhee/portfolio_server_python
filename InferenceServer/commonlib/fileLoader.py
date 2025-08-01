from operator import index
import os
import pickle
from typing import *
from PIL import Image
from glob import glob
import numpy as np
import json
import json5
import ast
import cv2

from commonlib.util.dataIterator import DataIterator


# ai 에서 필요한 파일 로드.
class FileLoader:
    def __init__(self):
        pass

    @staticmethod
    def loadPca(positionType: str):
        from commonlib.gconf import PcaData, gconf
        pcaData: PcaData = gconf.pcaDataDic[positionType]
        pcaDirPath: str = os.path.join(pcaData.dirPath, pcaData.fileName)

        pkl_file = open(pcaDirPath, 'rb')
        pca = pickle.load(pkl_file)
        pkl_file.close()
        return pca

    @staticmethod
    def loadDataInfo(path: str):
        with open(path, 'r') as f:
            data = json.load(f)

        return data

    @staticmethod
    def loadImagesData():
        from commonlib.gconf import gconf
        dataLoader = {
            0: FileLoader.__loadImages,
            1: FileLoader.__loadMultiviewImages,
            2: FileLoader.__loadCamImages,
        }

        return dataLoader[gconf.inputData.dataType](gconf.inputData)

    def __loadImages(data):
        from commonlib.glog import glog
        # glog.info('Start loading images for inference...')

        max_load = 1000
        glog.info('Maximum data number set to:{}'.format(max_load))

        paths = glob('{}/*.jpg'.format(data.dirPath))
        pathLenth = len(paths)

        assert pathLenth > 0, "No images was found in the folder."
        count = 0
        images: List[Any] = []
        for path in paths:
            if count > max_load:
                break
            im = Image.open(path).convert('L')
            im = im.resize(
                (data.metaData.imageWidth, data.metaData.imageHeight))
            im = np.array(im)
            images.append(im)

            if count % 100 == 0:
                glog.info("{}-{} loaded..".format(count, pathLenth))

            count += 1

        glog.info("{} images loaded.".format(len(images)))

        dataIter = DataIterator(images, len(images))
        return iter(dataIter)

    def __loadMultiviewImages(data):

        from commonlib.glog import glog

        glog.info('Start loading multiview images for inference...')

        max_load = 100
        glog.info('Maximum data number set to:{}'.format(max_load))

        paths = [
            os.path.join(data.dirPath, d) for d in os.listdir(data.dirPath)
            if os.path.isdir(os.path.join(data.dirPath, d))
        ]

        assert len(paths) > 0, "No images was found in the folder."
        assert len(
            paths
        ) == data.metaData.numSplit, "Not enough viewpoints to make predictions"

        count = 0
        filenames: List[str] = os.listdir(paths[0])
        images: List[Any] = []
        for f in filenames:
            ims = []
            for path in paths:

                if count > max_load:
                    glog.info("{} images loaded.".format(max_load))

                    # return images
                    dataIter = DataIterator(images, len(images))
                    return iter(dataIter)

                im = Image.open(os.path.join(path, f)).convert('L')
                im = im.resize(
                    (data.metaData.imageWidth, data.metaData.imageHeight))

                # TODO: 추후 삭제.
                im = im.rotate(90, expand=True)
                im = np.array(im)
                ims.append(im)

            images.append(np.concatenate(ims, axis=0))

            count += 1

            if count % 100 == 0:
                glog.info("{} loaded..".format(count))

        glog.info("{} images loaded.".format(len(images)))

        # return images
        dataIter = DataIterator(images, len(images))
        return iter(dataIter)

    def __loadCamImages(data):
        from commonlib.glog import glog
        glog.info("Starting Camera Loader...")

        class CamIterator:
            def __init__(self, cam_index: int = 0):
                import EasyPySpin

                self.cam = EasyPySpin.VideoCapture(cam_index)
                self.cam.BinningHorizontal = 2
                self.cam.BinningVertical = 2

            def __iter__(self):
                return self

            def __next__(self):
                _, frame = self.cam.read()
                im = cv2.resize(frame, (384, 288))

                return im

        camIter = CamIterator()

        return iter(camIter)
