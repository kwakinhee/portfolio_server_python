import numpy as np

from typing import *
from commonlib.gconf import DataInfos
from commonlib.ai.model import Model


class AINode:
    """ AI Node is a wrapper for model class. 
    
    For simple ML models, it will simply be a wrapper for Model class.
    For more complicated ML models, it will perform tasks necessary for inference. ex) face_alignment, pca...
    """
    def __init__(self, model, dataInfos):
        self.model: Model = model
        self.dataInfos: DataInfos = dataInfos

    def predict(self, input: np.array):
        # from commonlib.glog import glog
        # glog.info("predict inference on input images")

        predicted_values = self.model.predict(input)

        y_elements = self.dataInfos.dataInfo["Y_ELEMENTS"]
        # assert len(predicted_values) == len(y_elements)

        prediction_elements: list[dict[str, Any]] = [{
            **y_elements[i], "value":
            predicted_values[i]
        } for i in range(len(predicted_values))]

        return prediction_elements
