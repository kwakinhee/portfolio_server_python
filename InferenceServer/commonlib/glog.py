from twisted.logger import (FilteringLogObserver, textFileLogObserver,
                            globalLogBeginner, FileLogObserver, ILogObserver,
                            LogLevelFilterPredicate, LogLevel, Logger)

from twisted.python import logfile

import sys
import time
from commonlib.util.gutil import createDirectory
from commonlib.gconf import gconf

levels = {
    'debug': LogLevel.debug,
    'info': LogLevel.info,
    'warn': LogLevel.warn,
    'error': LogLevel.error,
    'critical': LogLevel.critical
}


class CustomDailyLogFile(logfile.DailyLogFile):
    __rotateLength = 0
    __size = 0

    def shouldRotate(self):
        return self.toDate(
        ) > self.lastDate and self.__rotateLength and self.__size >= self.__rotateLength


class GLog:
    __logtargets = []

    def __init__(self):

        fileLogSaveDir: str = gconf.log.file.saveDir
        createDirectory(fileLogSaveDir)

        extension = time.strftime("%Y_%m_%d_%H")
        self.__logfile = logfile.DailyLogFile(
            extension + "." + gconf.processName, fileLogSaveDir)

        #self.__applyLogLevel()
        self.__logger = Logger("Ai")

    def debug(self, message: str):
        self.__logger.debug(message)

    def info(self, message: str):
        self.__logger.info(message)

    def warn(self, message: str):
        self.__logger.warn(message)

    def error(self, message: str):
        self.__logger.error(message)

    def critical(self, message: str):
        self.__logger.critical(message)

    def getLogger(self):
        return self.__logger

    def __applyLogLevel(self, application):
        self.__applyConsoleLogLevel(gconf.log.console.level, application)
        self.__applyFileLogLevel(gconf.log.file.level, application)

        globalLogBeginner.beginLoggingTo(self.__logtargets)

    def __applyConsoleLogLevel(self, newLevel: str, application):

        stdoutflo = FilteringLogObserver(
            textFileLogObserver(sys.stdout),
            predicates=[LogLevelFilterPredicate(levels[newLevel])])

        self.__logtargets.append(stdoutflo)

    def __applyFileLogLevel(self, newLevel: str, application):

        filelogflo = FilteringLogObserver(
            textFileLogObserver(self.__logfile),
            predicates=[LogLevelFilterPredicate(levels[newLevel])])

        self.__logtargets.append(filelogflo)

        application.setComponent(ILogObserver,
                                 textFileLogObserver(self.__logfile))

    def Init(self, application):
        self.__applyLogLevel(application)


glog = GLog()
