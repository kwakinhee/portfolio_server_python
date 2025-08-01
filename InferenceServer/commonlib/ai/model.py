import os
import numpy as np

import tensorflow as tf

from commonlib.gconf import ModelData


class Model:
    """ ML Model class
    
    This class will be in charge of loading a single model and making an inference
    """
    def __init__(self, modelData: ModelData):
        self.init(modelData.modelName, modelData.path, modelData.metaData)

    def init(self, modelName: str, path: str, metaData: object):
        from commonlib.glog import glog
        glog.info("Loading model : %s" % modelName)
        self.model = tf.keras.models.load_model(os.path.join(path, modelName))

    def predict(self, data: np.array):
        data = np.expand_dims(data, axis=0).astype(np.uint8)
        data = np.expand_dims(data, axis=-1).astype(np.uint8)

        coef = self.model.predict(data).tolist()[0]

        return coef
