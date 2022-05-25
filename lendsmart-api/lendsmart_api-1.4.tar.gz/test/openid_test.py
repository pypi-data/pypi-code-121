import sys
sys.path.append('/home/lendsmart/code/lendsmart/workspace/py_lscommon/core_api/')
from ramda import path_or,is_empty,head
from lendsmart_api.lendsmart_client import LendsmartClient
from lendsmart_api.jwt.access_token.service_account import ServiceAccount
import traceback

api_endpoint = "https://devapi.lendsmart.ai/api/v1"
service_account_key = """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCfadx9PQyhEqu1
zkza8OPuF3jXaM2yDapbd5fwDzixRUcyBD8qlw0dQaaRDudGnrGP3oLH5+20pxi0
1JuMeDdu98dIWLu2m7aLSkEKZ3a+aZcywRPZACftMKcMVQQHIM8VGruFJ9P0CSHI
6eaGYpIjxBukaq+GXAG8GLv1HXxlQgdwiO8Tilr1F5cSfn5OIZB2rX4p1F1uZcFp
kNkK23qsohT28UM3+/tuBgn++H7sYlCJMih1wd9dnTji/5hzXXivCfSCfHBqXaWR
DRl1dVSqV2jflE3xzudUkdHRubdUpmN0BFZSA2QVSY19TPzbZWk8A7rswafc/c2i
XphamWmRAgMBAAECggEAYEtuKSjLjDDfEH+B5W9F//ilwllIh5nBombnnNdVA6A5
lXkDPxLnlRinKVC7W+lYkPN0RJVQ/aNCRVl4bK3hrmJ2Orl/Cpuc9R7xkvtUu0jF
UJ9ZAegaNikBf22LdVLYRINVauXYHr21bsv7uImqhXhcykC3ro29boXyY+pfzjnU
YVUE6FGlrdU+0ZpwCddlDXSdH3IVZpIQAyjOy1Vcve31Qb6BvRVzRx06uTAQx1ee
NAs/htX797JKk4u6FlQIkp/BDesT8IBCCxzfrIUv0kNpl1GgtlPCQcFlV+tO5XhP
cf9EY8Oe1UwvHzDH884pDxuvN0XottH6DQHOUOkbEQKBgQDQJ2LNOBnQCc/IZnAN
SePJzbW0Obpzm8suedRx3R8f4zA+MluwngBT9BTEJmSfmU/9K8I9uPVcKXBF7Cc1
YcG9A5rh9kOvOvhSLU0Nin+U4X+DjD/gc9EOW7t6II8CcwhD1r5c/RdFYOn0k9Mr
pY08NAbONH5MayeeB3SePbQmrwKBgQDEDmWyi5lsr0BhIp62uYrxVYm15Bq1spWr
I7jfYQciTJiKVaULTABBjxkRwuIu5LkM9XHcFWhQUE27pmLDBRnkB6vi8VUreRaF
KSTUeiADP2uENI3F+0J3pxoD0xlvegccAQXIrulcflhGPzlCmt1ycs+/M5zhiBB7
tfH//iuDvwKBgHW4UKBPQgnuAp0LkgNx7mmK9WBf5ZrMWTSHoiZjL98Q1Y/XWxOf
x/+y4qusKuw4AIzl2oydteXRabWhwOrnxnHnQAjbBZxsdVPEWvd1hIHmpf73qoh9
95VvO6/uCfMQq3PyVuawHCEYljfEAoGEt0N9CPxFo8gEMfulq8ZyjxfxAoGBAIyY
nomZ3t64Fv0RrKvxBxjmdKlB+X2PohFmvq9Cj7EjKMkbfg5J5G0fR6UbEsT6NVJ7
ublQiMv/qp8FRRIB2H1UmwlWc/OHFIVN6iGNquNpWZsnbPwroZDY/qj7e+QbqHmG
qjUuah9wY7GMqW2ATYpDl4PQaZK61sdAxVkFVwNVAoGBAJcrhvOZRJfWmLWp80H0
msS5JSUNJhoAhz4a+Nu6U5olu4nujYH1kAiWDMQnRSdi+gjsUXoTErlxF+jW0HDk
nyPvpJ+jQOHx/f/9axBGDlWSWDjg41zMWeAg82GFyOYkeOnPWn5DWn18Ka68WAgH
PtKjZcbK+onu2Q9pkljc0rig
-----END PRIVATE KEY-----"""

l = LendsmartClient(ServiceAccount(service_account_key),api_endpoint)
l.set_ignore_not_found_error()
loan_app_id = '1725355111529373696'
try:
    openid = l.openids.get_openid_by_role_id(loan_app_id, 'copper_lead')
    print(openid)
except Exception as error:
    print("✘ -----openid get exceptions ------ ✘")
    exc_info = sys.exc_info()
    traceback.print_exception(*exc_info)
    print("✘ -----openid get got exceptions ------ ✘", error)
