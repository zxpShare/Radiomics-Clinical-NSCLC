import os

from src.Util import MyLog as log
from src.Util import Utilitis as util
from src.Util import Params as params

from cryptography.fernet import Fernet
from collections import OrderedDict
import nrrd
import numpy as np
import pickle
import pandas as pd
import io

def decryptMethodForNrrd(encryptedFile, encryptedFileHeader, token):
    log.info('decryptMethodForNrrd encryptedFile:%s, encryptedFileHeader:%s, token:%s' % (encryptedFile, encryptedFileHeader, token,))

    if util.checkExist(encryptedFile) is False:
        return ValueError( 'decryptMethodForNrrd file is not exist: %s' % encryptedFile)

    if util.checkExist(encryptedFileHeader) is False:
        return ValueError('decryptMethodForNrrd file is not exist: %s' % encryptedFileHeader)

    if util.checkNoneOrEmptyForStr(token) is True:
        return ValueError( 'decryptMethodForNrrd token is empty.')

    cipherSuite = Fernet(token)

    with open(encryptedFile, 'rb') as file:
        encryptedData = file.read()

    decryptedData = cipherSuite.decrypt(encryptedData)
    log.info('decryptMethodForNrrd decryptedData type:%s' % (type(decryptedData, )))

    with open(encryptedFileHeader, 'rb') as file:
        encryptedHeader = file.read()

    decryptedHeader = cipherSuite.decrypt(encryptedHeader)
    log.info('decryptMethodForNrrd decryptedHeader type:%s' % (type(decryptedHeader, )))

    decryptedDictHeader = OrderedDict(pickle.loads(decryptedHeader))
    log.info('decryptMethodForNrrd decryptedDictHeader:%s' % (decryptedDictHeader,))

    listShape = decryptedDictHeader['sizes']
    if util.checkBufferSizeFromShape(len(decryptedData), listShape) is False:
        decryptedDataNdarray = np.frombuffer(decryptedData, dtype=np.int16)
    else:
        decryptedDataNdarray = np.frombuffer(decryptedData, dtype=np.int32)

    decryptedShape = tuple(listShape)
    log.info('decryptMethodForNrrd decryptedShape:%s' % (decryptedShape,))

    decryptedDataNdarray3D = decryptedDataNdarray.reshape(decryptedShape)

    fileName = os.path.basename(encryptedFile)
    directoryPath = os.path.dirname(encryptedFile)

    directoryPath = directoryPath.replace(params.encryptNodeName, params.decryptNodeName) + '/'
    if util.checkExist(directoryPath) is False:
        util.createDir(directoryPath)

    fileName = fileName.split('.')[0]
    fileName = fileName.replace(params.prefixEncryptName, params.prefixDecryptName) + '.nrrd'
    decryptedFile = directoryPath + fileName

    nrrd.write(filename=decryptedFile,
               data=decryptedDataNdarray3D,
               header=decryptedDictHeader)
    log.info('decryptMethodForNrrd write to file:%s' % (decryptedFile,))

    return decryptedFile


def decryptMethodForXlsx(encryptedFile, token):
    log.info('decryptMethodForXlsx encryptedFile:%s, token:%s' % (encryptedFile, token,))

    if util.checkExist(encryptedFile) is False:
        return ValueError( 'decryptMethodForXlsx file is not exist: %s' % encryptedFile)

    if util.checkNoneOrEmptyForStr(token) is True:
        return ValueError( 'decryptMethodForXlsx token is empty.')

    with open(encryptedFile, 'rb') as file:
        encryptedData = file.read()

    cipherSuite = Fernet(token)

    decryptedData = cipherSuite.decrypt(encryptedData)
    log.info('decryptMethodForXlsx decryptedData type:%s' % (type(decryptedData, )))

    dfDecryptedData = pd.read_csv(io.BytesIO(decryptedData))

    fileName = os.path.basename(encryptedFile)
    directoryPath = os.path.dirname(encryptedFile)
    directoryPath = directoryPath.replace(params.encryptNodeName, params.decryptNodeName) + '/'

    if util.checkExist(directoryPath) is False:
        util.createDir(directoryPath)

    fileName = fileName.split('.')[0]
    fileName = fileName.replace(params.prefixEncryptName, params.prefixDecryptName) + '.xlsx'
    decryptedFile = directoryPath + fileName

    dfDecryptedData.to_excel(decryptedFile)
    log.info('decryptMethodForXlsx write to file:%s' % (decryptedFile,))

    return decryptedFile
