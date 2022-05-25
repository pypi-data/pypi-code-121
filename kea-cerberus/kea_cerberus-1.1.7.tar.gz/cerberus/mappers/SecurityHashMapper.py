
from cerberus.dtos.SecurityHash import SecurityHash

class SecurityHashMapper():

    def mapToSecurityHash(ksmSecurityHash):
        securityHash = SecurityHash(ksmSecurityHash.getToken(), ksmSecurityHash.getSecurityHashTypeId(), ksmSecurityHash.getUsed(), ksmSecurityHash.getActive())
        return securityHash
