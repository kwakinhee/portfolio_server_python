import os
from typing import *
import time


def createDirectory(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print("Failed to create the directory.")


def curTimeUtc():
    return round(time.time())
