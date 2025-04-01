import os
import pandas as pd
import time
import sys


from src.Util import Params as params
from src.Fernet import KeyImplement as keyImpl, EncryptImplement as encryptImpl
from src.Fernet import DecryptImplement as decryptImpl
from src.Analysis import AnalysisImplement as analysisImpl
from src.Radiomics import ExtractRadiomicsFeatures as extract


def encryptTask():
    tokenDataNrrd = encryptForNrrd()
    tokenDataClinical = encryptForClinical()

    tokenData = pd.concat([tokenDataNrrd, tokenDataClinical], axis=0) 
    tokenData.columns = [params.patiendIDNodeName, params.tokenNodeName,
                         params.executionTime % 'original', params.executionTime % '2D',
                         params.executionTime % '3D', params.executionTime % 'peritumoral']

    tokenData.to_excel(params.tokenFilePath)
    log.info('encryptTask write to file:%s' % (params.tokenFilePath,))

def decryptTask():

    tokenData = decryptForNrrd()

    tokenData.columns = [params.patiendIDNodeName, params.executionTime % 'original', params.executionTime % '2D',
                         params.executionTime % '3D', params.executionTime % 'peritumoral',
                         params.extractTime % '2D', params.extractTime % '3D', params.extractTime % 'peritumoral']
    tokenData.to_excel(params.decryptFilePath)
    log.info('decryptTask write to file:%s' % (params.decryptFilePath,))

def encryptForNrrd():

    tokenData = None
    path = params.nrrdDataPath
    dirs = os.listdir(path)
    for dirNode in dirs:
        log.debug('encryptForNrrd dirNode:' + dirNode)

        if os.path.isdir(path + dirNode) and not dirNode.startswith('.'):
            files = os.listdir(path + dirNode)

            if dirNode.startswith('R') is True:
                patientID = dirNode
            else:
                patientID = dirNode.split('_')[0]

            token = keyImpl.generateKeyFromPassword(patientID.encode())
            log.debug('encryptForNrrd token:%s' % (token,))

            executionTimeArray = [0.0] * 4  # original, 2D, 3D, peritumoral

            for file in files:
                imgFile = ''
                if not os.path.isdir(path + dirNode + '/' + file) and not file.startswith('.'):
                    if not 'nrrd' in file:
                        continue

                    imgFile = file
                    nrrdFile = (path + dirNode + '/' + imgFile)
                    log.debug('encryptForNrrd nrrdFile:%s' % (nrrdFile,))

                    startTime = time.time()
                    encryptImpl.encryptMethodForNrrd(nrrdFile, token)
                    endTime = time.time()
                    executionTime = '%.1f' % (endTime - startTime)  # (s)

                    if '2D' in file:
                        executionTimeArray[1] = executionTime
                    elif 'Final_mask' in file:
                        executionTimeArray[2] = executionTime
                    elif 'peritumoral' in file:
                        executionTimeArray[3] = executionTime
                    else: # 'original'
                        executionTimeArray[0] = executionTime

            tokenStr = token.decode()

            dfData = pd.DataFrame([patientID, tokenStr, executionTimeArray[0], executionTimeArray[1],
                                   executionTimeArray[2], executionTimeArray[3]]).T
            if tokenData is None:
                tokenData = dfData
            else:
                tokenData = pd.concat([tokenData, dfData], axis=0) 

    return tokenData

def encryptForClinical():

    tokenData = None
    path = params.clinicalDataPath
    files = os.listdir(path)
    for file in files:
        log.debug('encryptForClinical file:' + file)

        if not os.path.isdir(path + file) and not file.startswith('.') and file.endswith('.xlsx'):
            xlsxFile = file
        else:
            continue

        clinicalFile = (path + xlsxFile)
        log.debug('encryptForClinical clinicalFile:%s' % (clinicalFile,))

        fileName = os.path.basename(xlsxFile)
        token = keyImpl.generateKeyFromPassword(fileName.encode())
        log.debug('encryptForClinical token:%s' % (token,))

        encryptImpl.encryptMethodForXlsx(clinicalFile, token)
        tokenStr = token.decode()

        dfData = pd.DataFrame([fileName, tokenStr]).T
        if tokenData is None:
            tokenData = dfData
        else:
            tokenData = pd.concat([tokenData, dfData], axis=0)  

    return tokenData

def decryptForNrrd():
    log.info('decryptForNrrd....')

    tokenData = None
    path = params.nrrdDataPath
    dirs = os.listdir(path)
    for dirNode in dirs:
        log.debug('decryptForNrrd dirNode:' + dirNode)

        if os.path.isdir(path + dirNode) and not dirNode.startswith('.'):
            encryptDirPath = path + dirNode + ('/%s/' % params.encryptNodeName)
            files = os.listdir(encryptDirPath)

            imgFile = [''] * 4
            headerFile = [''] * 4
            for file in files:
                if not os.path.isdir(path + dirNode + '/' + file) and not file.startswith('.'):
                    if 'nrrd' in file:
                        continue

                    if params.prefixEncryptName in file:
                        if '2D' in file:
                            imgFile[1] = file
                        elif 'Final_mask' in file:
                            imgFile[2] = file
                        elif 'peritumoral' in file:
                            imgFile[3] = file
                        else:  # 'original'
                            imgFile[0] = file
                    elif params.prefixHeaderName in file:
                        if '2D' in file:
                            headerFile[1] = file
                        elif 'Final_mask' in file:
                            headerFile[2] = file
                        elif 'peritumoral' in file:
                            headerFile[3] = file
                        else:  # 'original'
                            headerFile[0] = file
                    else:
                        continue

            if dirNode.startswith('R') is True:
                patientID = dirNode
            else:
                patientID = dirNode.split('_')[0]
            token = keyImpl.queryTokenFromePassword(patientID)

            executionTimeArray = [0] * 4
            decryptedFileArray = [''] * 4
            for i in range(4):
                encryptedFile = encryptDirPath + imgFile[i]
                encryptedFileHeader = encryptDirPath + headerFile[i]

                startTime = time.time()
                decryptedFileArray[i] = decryptImpl.decryptMethodForNrrd(encryptedFile, encryptedFileHeader, token)
                endTime = time.time()
                executionTime = '%.1f' % (endTime - startTime)  # (s)

                executionTimeArray[i] = executionTime

            extractTimeArray = [0] * 3
            for i in range(4):
                if i == 0: # 2D
                    startTime = time.time()
                    extract.featureExtractBySettings(decryptedFileArray[0],decryptedFileArray[1], [0.8, 0.8, 0.8])
                    endTime = time.time()
                    executionTime = '%.1f' % (endTime - startTime)  # (s)

                    extractTimeArray[i] = executionTime
                elif i == 1: # 3D
                    startTime = time.time()
                    extract.featureExtractBySettings(decryptedFileArray[0], decryptedFileArray[2], [1.0, 1.0, 1.0])
                    endTime = time.time()
                    executionTime = '%.1f' % (endTime - startTime)  # (s)

                    extractTimeArray[i] = executionTime
                elif i == 2:  # peritumoral
                    startTime = time.time()
                    extract.featureExtractBySettings(decryptedFileArray[0], decryptedFileArray[3], [1.0, 1.0, 1.0])
                    endTime = time.time()
                    executionTime = '%.1f' % (endTime - startTime)  # (s)

                    extractTimeArray[i] = executionTime

            dfData = pd.DataFrame([patientID, executionTimeArray[0], executionTimeArray[1],
                                   executionTimeArray[2], executionTimeArray[3],
                                  extractTimeArray[0], extractTimeArray[1], extractTimeArray[2]]).T

            if tokenData is None:
                tokenData = dfData
            else:
                tokenData = pd.concat([tokenData, dfData], axis=0)  


    return tokenData

def decryptForClinical():
    log.info('decryptForClinical....')

    path = params.clinicalDataPath
    dirs = os.listdir(path)
    for dirNode in dirs:
        log.debug('decryptForClinical dirNode:' + dirNode)

        if os.path.isdir(path + dirNode) and not dirNode.startswith('.'):
            encryptDirPath = path + dirNode + '/'
            files = os.listdir(encryptDirPath)

            xlsxFile = ''
            for file in files:
                if not os.path.isdir(path + file) and not file.startswith('.'):
                    xlsxFile = file
                else:
                    continue

            fileName = os.path.basename(xlsxFile)
            password = fileName.split('.')[0]
            password = password.split(params.prefixEncryptName)[1] + '.xlsx'
            token = keyImpl.queryTokenFromePassword(password)

            encryptedFile = encryptDirPath + xlsxFile
            decryptImpl.decryptMethodForXlsx(encryptedFile, token)

def analysisForNrrd():
    log.info('analysisForNrrd....')

    analysisResult = None
    path = params.nrrdDataPath
    dirs = os.listdir(path)
    for dirNode in dirs:
        log.debug('analysisForNrrd dirNode:' + dirNode)

        if os.path.isdir(path + dirNode) and not dirNode.startswith('.'):
            originalFile = ''
            originalDirPath = path + dirNode + '/'
            files = os.listdir(originalDirPath)
            for file in files:
                if not os.path.isdir(path + dirNode + '/' + file) and not file.startswith('.'):
                    if not 'nrrd' in file:
                        continue

                    if '3D' in file or 'label' in file or 'Final_mask' in file or 'peritumoral' in file:
                        continue
                    else:
                        originalFile = file
            originalFile = originalDirPath+ originalFile

            encryptedFile = ''
            encryptDirPath = path + dirNode + ('/%s/' % params.encryptNodeName)
            files = os.listdir(encryptDirPath)
            for file in files:
                if not os.path.isdir(path + dirNode + '/' + file) and not file.startswith('.'):
                    if 'nrrd' in file:
                        encryptedFile = file
                    else:
                        continue
            encryptedFile = encryptDirPath + encryptedFile

            decryptedFile = ''
            decryptDirPath = path + dirNode + ('/%s/' % params.decryptNodeName)
            files = os.listdir(decryptDirPath)
            for file in files:
                if not os.path.isdir(path + dirNode + '/' + file) and not file.startswith('.'):
                    if 'nrrd' in file:
                        decryptedFile = file
                    else:
                        continue
            decryptedFile = decryptDirPath + decryptedFile

            if dirNode.startswith('R') is True:
                patientID = dirNode
            else:
                patientID = dirNode.split('_')[0]

            ssimScore = analysisImpl.caculateSSIM(originalFile, decryptedFile)
            horizontal_coef_original, vertical_coef_original, diagonal_coef_original = analysisImpl.correlationForNrrd(originalFile)
            horizontal_coef_encrypted, vertical_coef_encrypted, diagonal_coef_encrypted = analysisImpl.correlationForNrrd(encryptedFile)
            horizontal_coef_decrypted, vertical_coef_decrypted, diagonal_coef_decrypted = analysisImpl.correlationForNrrd(decryptedFile)

            analysisImpl.validationForNrrd(originalFile, encryptedFile, decryptedFile)

            dfData = pd.DataFrame([patientID, ssimScore,
                                   horizontal_coef_original, vertical_coef_original, diagonal_coef_original,
                                   horizontal_coef_encrypted, vertical_coef_encrypted, diagonal_coef_encrypted,
                                   horizontal_coef_decrypted, vertical_coef_decrypted, diagonal_coef_decrypted]).T

            if analysisResult is None:
                analysisResult = dfData
            else:
                analysisResult = pd.concat([analysisResult, dfData], axis=0) 

    columnNameList = [params.patiendIDNodeName, params.ssimNodeName,
                  params.horizontalNodeName % params.originalNodeName,
                  params.verticalNodeName % params.originalNodeName, params.diagonalNodeName % params.originalNodeName,
                  params.horizontalNodeName % params.encryptNodeName, params.verticalNodeName % params.encryptNodeName,
                  params.diagonalNodeName % params.encryptNodeName,
                  params.horizontalNodeName % params.decryptNodeName, params.verticalNodeName % params.decryptNodeName,
                  params.diagonalNodeName % params.decryptNodeName]
    analysisResult.columns = columnNameList

    analysisResult.to_excel(params.analysisFilePath)


if __name__ == '__main__':
    log.info('............')
    # encryptTask()

    keyImpl.loadToken()
    decryptTask()

    analysisForNrrd()








