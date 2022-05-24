#
#  Copyright (c) 2018-2022 Renesas Inc.
#  Copyright (c) 2018-2022 EPAM Systems Inc.
#


class OnBoardingError(Exception):
    pass


class UserCredentialsError(OnBoardingError):
    pass


class DeviceRegisterError(OnBoardingError):
    pass


class DeviceDeregisterError(OnBoardingError):
    pass


class BoardError(OnBoardingError):
    pass


class GrpcUnimplemented(OnBoardingError):
    pass


class CloudAccessError(OnBoardingError):
    pass


class AosProvError(OnBoardingError):
    pass
