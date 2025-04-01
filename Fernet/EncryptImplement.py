import os
from src.Util import MyLog as log
from src.Util import Utilitis as util
from src.Util import Params as params

from cryptography.fernet import Fernet
import pickle
import nrrd
import numpy as np
import pandas as pd

def encryptMethodForNrrd(nrrdFile, token):
    log.info('encryptMethodForNrrd nrrdFile:%s, token:%s' % (nrrdFile, token,))

    if util.checkExist(nrrdFile) is False:
        return ValueError('encryptMethodForNrrd file is not exist:%s' % nrrdFile)

    nrrd_file, header = nrrd.read(nrrdFile)
    log.info('encryptMethodForNrrd nrrd_file type:%s, shape:%s, header:%s' % (type(nrrd_file), nrrd_file.shape, header,))

    if util.checkNoneOrEmptyForStr(token) is True:
        return ValueError('encryptMethodForNrrd token is empty.')
    cipherSuite = Fernet(token)

    nrrdDataBytes = nrrd_file.tobytes()
    log.info('encryptMethodForNrrd type nrrdDataBytes:%s' % (type(nrrdDataBytes, )))
    encryptedData = cipherSuite.encrypt(nrrdDataBytes)

    nrrdHeaderBytes = pickle.dumps(header)
    log.info('encryptMethodForNrrd type nrrdHeaderBytes:%s' % (type(nrrdHeaderBytes, )))
    encryptedHeader = cipherSuite.encrypt(nrrdHeaderBytes)

    fileName = os.path.basename(nrrdFile)
    directoryPath = os.path.dirname(nrrdFile)

    encryptedFilePath = directoryPath + ('/%s/' % params.encryptNodeName)
    if util.checkExist(encryptedFilePath) is False:
        util.createDir(encryptedFilePath)

    encryptedFile = encryptedFilePath + ('%s' % params.prefixEncryptName) + fileName
    log.info('encryptMethodForNrrd nrrdDataBytes.length:%s, encryptedData.length:%s' % (len(nrrdDataBytes), len(encryptedData),))

    encryptedDataTemp = encryptedData[:len(nrrdDataBytes)]
    if util.checkBufferSizeFromShape(len(encryptedDataTemp), list(nrrd_file.shape)) is False:
        ndarray_int32_temp = np.frombuffer(encryptedDataTemp, dtype=np.int16)
    else:
        ndarray_int32_temp = np.frombuffer(encryptedDataTemp, dtype=np.int32)
    log.info('encryptMethodForNrrd encryptedDataTemp.lenth:%s' % (len(encryptedDataTemp),))

    ndarray_int32_temp = ndarray_int32_temp.reshape(nrrd_file.shape)
    nrrd.write(filename=encryptedFile,
               data=ndarray_int32_temp,
               header=header)
    log.info('encryptMethodForNrrd write to file:%s' % (encryptedFile,))

    encryptedFile = encryptedFilePath + ('%s' % params.prefixEncryptName) + fileName.split('.')[0] + '.pickle'
    with open(encryptedFile, 'wb') as file:
        file.write(encryptedData)
        log.info('encryptMethodForNrrd write to file:%s' % (encryptedFile,))

    encryptedFileHeader = encryptedFilePath + ('%s' % params.prefixHeaderName) + fileName.split('.')[0] + '.pickle'
    with open(encryptedFileHeader, 'wb') as file:
        file.write(encryptedHeader)
        log.info('encryptMethodForNrrd write to file:%s' % (encryptedFileHeader,))

    return encryptedFile, encryptedFileHeader

def encryptMethodForXlsx(xlsxFile, token):
    log.info('encryptMethodForXlsx xlsxFile:%s, token:%s' % (xlsxFile, token,))

    if util.checkExist(xlsxFile) is False:
        return ValueError('encryptMethodForXlsx file is not exist:%s' % xlsxFile)

    if util.checkNoneOrEmptyForStr(token) is True:
        return ValueError('encryptMethodForXlsx token is empty.')
    cipherSuite = Fernet(token)

    data = pd.read_excel(xlsxFile, index_col=0)  
    dataBytes = data.to_csv(index=False).encode()
    log.info('encryptMethodForXlsx type dataBytes:%s' % (type(dataBytes, )))
    encryptetData = cipherSuite.encrypt(dataBytes)

    fileName = os.path.basename(xlsxFile)
    directoryPath = os.path.dirname(xlsxFile)

    encryptedFilePath = directoryPath + '/%s/' % params.encryptNodeName
    if os.path.exists(encryptedFilePath) is False:
        os.makedirs(encryptedFilePath)

    encryptedFile = encryptedFilePath + '%s' % params.prefixEncryptName + fileName.split('.')[0] + '.pickle'
    with open(encryptedFile, 'wb') as file:
        file.write(encryptetData)
        log.info('encryptMethodForXlsx write to file:%s' % (encryptedFile,))

    return encryptedFile
