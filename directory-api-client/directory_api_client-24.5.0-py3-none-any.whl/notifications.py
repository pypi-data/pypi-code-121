from directory_api_client.base import AbstractAPIClient

url_unsubscribe = '/notifications/anonymous-unsubscribe/'


class NotificationsAPIClient(AbstractAPIClient):
    def anonymous_unsubscribe(self, uidb64, token):
        return self.post(url=url_unsubscribe, data={'uidb64': uidb64, 'token': token})
