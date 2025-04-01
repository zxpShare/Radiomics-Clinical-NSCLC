
from src.Util import Params as params
from src.Util import MyLog as log
from src.Util import Utilitis as util

import os
import numpy as np
import cv2


def saveImageFromSlide(slideNumber, nrrdFilePath, imgArr, type):
    log.info('saveImageFromSlide slideNumber:%s, nrrdFilePath:%s, imgArr size:%s,' % (slideNumber, nrrdFilePath, len(imgArr),))

    dirPath = os.path.dirname(nrrdFilePath)
    imgDirPath = dirPath + ('/%s/' % params.slideImgNodeName)
    if util.checkExist(imgDirPath) is False:
        util.createDir(imgDirPath)

    if type == 0:
        imgFileName = params.prefixCoeImgName % slideNumber + '.jpg'
    elif type == 1: 
        imgFileName = params.prefixSlideImgName % slideNumber + '.jpg'

    filePath = imgDirPath + imgFileName

    rotateImgArr = cv2.rotate(imgArr, cv2.ROTATE_90_CLOCKWISE) 
    high = np.max(rotateImgArr)
    low = np.min(rotateImgArr)

    convert_from_dicom_to_jpg(rotateImgArr, low, high, filePath) 
    log.info('saveImageFromSlide write slice data: %s' % (filePath,))


def convert_from_dicom_to_jpg(img, low_window, high_window, save_path):
    lungwin = np.array([low_window*1.,high_window*1.])
    newimg = (img-lungwin[0])/(lungwin[1]-lungwin[0]) 
    newimg = (newimg*255).astype('uint8')     
    cv2.imwrite(save_path, newimg, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

