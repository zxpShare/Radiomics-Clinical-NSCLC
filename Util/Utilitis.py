import os
import shutil

from src.Util import MyLog as log


def createDir(path):
    log.info('createDir path:' + path)
    path = path.strip()

    path = path.rstrip("\\")

    isExists = os.path.exists(path)

    if not isExists:
        os.makedirs(path)
        log.debug('mkdir path:' + path)

        return True
    else:
        log.debug('exist path:' + path)

        return False


def checkExist(dirPath):
    if os.path.exists(dirPath):
        return True
    else:
        return False

def checkNoneOrEmptyForStr(str):
    if str is None or str == '':
        return True
    else:
        return False

def removeFile(filePath):
    if os.path.exists(filePath):
        os.remove(filePath)

def deleteDirs(dirPath):
    if os.path.exists(dirPath):
        shutil.rmtree(dirPath)

def checkBufferSizeFromShape(bufferLen, listShape):
    requestSize = (listShape[0] * listShape[1] * listShape[2] * 4)
    if  bufferLen !=  requestSize:
        return False
    else:
        return True