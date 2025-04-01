from radiomics import featureextractor

from src.Util import MyLog as log


def featureExtract(imagePath, maskPath):
    log.info('featureExtract imagePath:' + imagePath + ' maskPath:' + maskPath)
    extractor = featureextractor.RadiomicsFeatureExtractor()

    return extractor.execute(imagePath, maskPath)

def featureExtractBySettings(imagePath, maskPath, resampledPixelSpacing):
    log.info(
        'featureExtractBySettings imagePath:' + imagePath + ' maskPath:' + maskPath + ' resampledPixelSpacing:' + str(
            resampledPixelSpacing))

    settings = {}
    settings['binWidth'] = 25
    settings['interpolator'] = 'sitkBSpline'
    settings['resampledPixelSpacing'] = resampledPixelSpacing
    # settings['resampledPixelSpacing'] = [2.5, 2.5, 2.5]
    # settings['resampledPixelSpacing'] = None
    settings['verbose'] = True

    extractor = featureextractor.RadiomicsFeatureExtractor(**settings)

    extractor.enableImageTypeByName('Wavelet')

    return extractor.execute(imagePath, maskPath)