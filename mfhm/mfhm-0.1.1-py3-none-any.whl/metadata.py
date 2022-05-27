class TransmissionType(object):
    '''
    传输类型
    '''
    
    # 服务密钥类型, 表示服务开启了服务密钥验证
    authKey = 'key'

    # 服务密钥 + RSA加密类型, 表示服务在服务密钥的基础上开启了RSA加密
    # authKeyRsa = 'key-rsa'

    @classmethod
    def all(cls) -> tuple:
        '''
        返回所有传输类型
        '''
        return (
            cls.authKey,
            # cls.authKeyRsa
        )


class TransmissionTypeField(object):
    '''
    传输类型所对应的字段
    '''
    # 传输类型对应的HTTP头字段名称
    headers = {
        TransmissionType.authKey: 'MFHM-AuthKey'
    }