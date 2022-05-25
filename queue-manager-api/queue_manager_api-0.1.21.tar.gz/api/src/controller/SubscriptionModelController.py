from python_framework import Controller, ControllerMethod, HttpStatus

from enumeration.AccessDomain import AccessDomain
import SubscriptionDto


@Controller(url = '/subscription', tag='Subscription', description='Subscription controller')
class SubscriptionModelController:

    @ControllerMethod(url = '/',
        apiKeyRequired = [AccessDomain.API],
        responseClass = [[SubscriptionDto.SubscriptionResponseDto]]
        # , logRequest = True
        # , logResponse = True
    )
    def get(self):
        return self.service.subscriptionModel.findAllByOrigin(), HttpStatus.OK


    @ControllerMethod(url = '/',
        apiKeyRequired = [AccessDomain.API],
        requestClass = [SubscriptionDto.SubscriptionRequestDto],
        responseClass = [SubscriptionDto.SubscriptionResponseDto]
        # , logRequest = True
        # , logResponse = True
    )
    def post(self, dto):
        return self.service.subscriptionModel.createOrUpdate(dto), HttpStatus.CREATED
