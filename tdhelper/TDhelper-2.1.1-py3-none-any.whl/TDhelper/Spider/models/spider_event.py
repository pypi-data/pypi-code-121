from enum import Enum

class event(Enum):
    onError= 'error'
    onIndexComplete= 'indexcomplete'
    onListComplete= 'listcomplete'
    onDetailComplete= 'detailcomplete'
    onFingerprintComplete= 'fingerprintcomplete'
    onDebug= 'debug'