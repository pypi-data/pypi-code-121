import firebase_admin
from firebase_admin import auth, credentials
from cerberus.exceptions.exceptions import InvalidUserCredentialsException, NotFoundUserException

class FirebaseService():

    def __init__(self,firebaseCredential):
        cred = credentials.Certificate(firebaseCredential)
        if (not len(firebase_admin._apps)):
            default_app = firebase_admin.initialize_app(cred)

    def getDecoded_token(self, tokenId):
        try:
            decoded_token = auth.verify_id_token(tokenId)
        except Exception as error:
            raise InvalidUserCredentialsException()

        return decoded_token

    def getProviderIdByEmail(self,email):
        try:
            user = auth.get_user_by_email(email)
            providers = []
            for i in user.provider_data:
                providers.append(i.provider_id)

        except Exception as error:
            print(error)
        
        return providers
