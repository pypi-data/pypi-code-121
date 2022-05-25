import json

class talk_with_cognito():
    def __init__(self, boto_client, cognito_user_pool_id, debug=False):
        self.boto_client = boto_client
        self.cognito_user_pool_id = cognito_user_pool_id
        self.debug = debug
    def get_user_email(self, cognito_user_id):
        cognito_response = self.boto_client.admin_get_user(
            UserPoolId=self.cognito_user_pool_id,
            Username=cognito_user_id
        )

        if self.debug:
            print("Cognito Response: {}".format(json.dumps(cognito_response,  default=str)))

        cognito_response        = json.loads(json.dumps(cognito_response,  default=str))

        cognito_email_verified  = None
        cognito_user_email      = None

        for data in cognito_response['UserAttributes']:
            if data['Name'] == 'email':
                cognito_user_email = data['Value']
            elif data['Name'] == 'email_verified':
                cognito_email_verified  = data['Value']
                if cognito_email_verified == 'true':
                    cognito_email_verified = True
                else:
                    cognito_email_verified = False

        return cognito_user_email, cognito_email_verified
