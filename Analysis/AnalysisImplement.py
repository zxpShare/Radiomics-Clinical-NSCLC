from src.Util import MyLog as log
from src.Util import Utilitis as util
from src.Analysis import ImgOperation as imgOperate
from skimage.metrics import structural_similarity as ssim

import matplotlib.pyplot as plt
import numpy as np
import nrrd
import random
import cv2


def corrlelationForImg(image, direction): 
    m = image.shape[0]
    n = image.shape[1]
    X = np.zeros((m, n))

    if direction == 1:
        X = np.hstack((image[:, n - 1].reshape(-1, 1), image[:, :n - 1]))  
        log.info('corrlelationForImg horizontal correlation coefficient:%s' % np.corrcoef(image.ravel(),X.ravel())[0][1])

        return np.corrcoef(image.ravel(), X.ravel())[0][1]

    if direction == 2:
        X = np.vstack((image[m - 1, :].reshape(1, -1), image[:m - 1, :]))
        log.info('corrlelationForImg vertical correlation coefficient:%s' % np.corrcoef(image.ravel(),X.ravel())[0][1])

        return np.corrcoef(image.ravel(), X.ravel())[0][1]

    if direction == 3:
        X = np.hstack((image[:, n - 1].reshape(-1, 1), image[:, 0:n - 1]))
        X = np.vstack((X[m - 1, :].reshape(1, -1), X[:m - 1, :]))
        log.info('corrlelationForImg diagonal correlation coefficient:%s' % np.corrcoef(image.ravel(),X.ravel())[0][1])

        return np.corrcoef(image.ravel(), X.ravel())[0][1]

def showCorrlelationForImgArr(image, direction):
    m = image.shape[0]
    n = image.shape[1]
    X = np.zeros((m, n))

    if direction == 1:
        X = np.hstack((image[:, n - 1].reshape(-1, 1), image[:, :n - 1])) 

        plt.figure()
        plt.scatter(image.ravel(), X.ravel(), marker='.', s=0.1)
        plt.xlabel('Gary vale of pixel location(a,b)')
        plt.ylabel('Gary vale of pixel location(a+1,b)')
        plt.show()

        return np.corrcoef(image.ravel(), X.ravel())[0][1]

    if direction == 2:
        X = np.vstack((image[m - 1, :].reshape(1, -1), image[:m - 1, :])) 

        plt.figure()
        plt.scatter(image.ravel(), X.ravel(), marker='.', s=0.1)
        plt.xlabel('Gary vale of pixel location(a,b)')
        plt.ylabel('Gary vale of pixel location(a,b+1)')
        plt.show()

        return np.corrcoef(image.ravel(), X.ravel())[0][1]

    if direction == 3:
        X = np.hstack((image[:, n - 1].reshape(-1, 1), image[:, 0:n - 1]))
        X = np.vstack((X[m - 1, :].reshape(1, -1), X[:m - 1, :]))

        plt.figure()
        plt.scatter(image.ravel(), X.ravel(), marker='.', s=0.1)
        plt.xlabel('Gary vale of pixel location(a,b)')
        plt.ylabel('Gary vale of pixel location(a+1,b+1)')
        plt.show()

        return np.corrcoef(image.ravel(), X.ravel())[0][1]


def correlationForNrrd(nrrdFile):
    log.info('correlationForNrrd nrrdFile:%s' % (nrrdFile,))

    nrrd_file, header = nrrd.read(nrrdFile)

    randomSlide = random.randint(0, nrrd_file.shape[2]-1)
    log.info('correlationForNrrd randomSlide:%s' % (randomSlide,))
    img = nrrd_file[:,:,randomSlide]

    imgOperate.saveImageFromSlide(randomSlide, nrrdFile, img, 0)

    horizontalCoef = corrlelationForImg(img, 1)
    verticalCoef = corrlelationForImg(img, 2)
    diagonalCoef = corrlelationForImg(img, 3)
    log.info('correlationForNrrd horizontalCoef:%s, verticalCoef:%s, diagonalCoef:%s' % (horizontalCoef, verticalCoef, diagonalCoef,))

    return horizontalCoef, verticalCoef, diagonalCoef

def showCorrelationForImg(imgFile):
    log.info('showCorrelationForImg imgFile:%s' % (imgFile,))

    img = cv2.imread(imgFile) 
    img2 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    direction = 1
    d1 = showCorrlelationForImgArr(img2, direction) 
    log.info('Horizontal correlation coefficient of Original image:%s' % (d1,))

    direction = 2
    d2 = showCorrlelationForImgArr(img2, direction) 
    log.info('Vertical correlation coefficient of Original image:%s' % (d2,))

    direction = 3 
    d3 = showCorrlelationForImgArr(img2, direction) 
    log.info('Diagonal correlation coefficient of Original image:%s' % (d3,))


def validationForNrrd(originalFile, encryptedFile, decryptedFile):

    nrrd_file_original, header_original = nrrd.read(originalFile)
    randomSlide = random.randint(0, nrrd_file_original.shape[2] - 1)
    img = nrrd_file_original[:, :, randomSlide]
    imgOperate.saveImageFromSlide(randomSlide, originalFile, img, 1)

    nrrd_file_encrypt, header_encrypt = nrrd.read(encryptedFile)
    img = nrrd_file_encrypt[:, :, randomSlide]
    imgOperate.saveImageFromSlide(randomSlide, encryptedFile, img, 1)

    nrrd_file_decrypt, header_decrypt = nrrd.read(decryptedFile)
    img = nrrd_file_decrypt[:, :, randomSlide]
    imgOperate.saveImageFromSlide(randomSlide, decryptedFile, img, 1)



def caculateSSIM(nrrdPath1, nrrdPath2):
    log.info('caculateSSIM nrrdPath1:%s, nrrdPath2:%s' % (nrrdPath1, nrrdPath2,))

    if util.checkExist(nrrdPath1) is False:
        return ValueError('caculateSSIM file is not exist:%s' % nrrdPath1)

    if util.checkExist(nrrdPath2) is False:
        return ValueError('caculateSSIM file is not exist:%s' % nrrdPath2)

    nrrd_file1, header1 = nrrd.read(nrrdPath1)
    nrrd_file2, header2 = nrrd.read(nrrdPath2)

    ssimScore = ssim(nrrd_file1, nrrd_file2, channel_axis=False)
    log.info('caculateSSIM ssim_score:%s' % (ssimScore,))

    return ssimScore