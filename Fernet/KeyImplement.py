import os
from src.Util import MyLog as log
from src.Util import Params as params
from src.Util import Utilitis as util

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import base64
import pandas as pd

tokenListDict = {}

def generateKeyFromPassword(bpassword):
    log.info('generateKeyFromPassword bpassword:%s' % (bpassword,))
    salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(bpassword))

    return key

def queryTokenFromePassword(password):
    log.info('queryTokenFromePassword password:%s' % (password,))

    if tokenListDict is None or not password in tokenListDict:
        return ValueError('queryTokenFromePassword password is not in dict:%s' % password)

    stoken = tokenListDict[password]
    token = stoken.encode()

    return token


def loadToken():
    log.info('loadToken......')

    if util.checkExist(params.tokenFilePath) is False:
        return ValueError('loadToken file is not exist:%s' % params.tokenFilePath)

    log.debug('loadToken params.tokenFilePath:%s' % params.tokenFilePath)
    dfData = pd.read_excel(params.tokenFilePath, index_col=0)  

    tokenListDict.clear()
    for index, row in dfData.iterrows():
        patientID = row[params.patiendIDNodeName]
        token = row[params.tokenNodeName]

        tokenListDict[patientID] = token

    log.info('loadToken tokenListDict:%s' % (tokenListDict,))


