from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse
from lantools.exception import SSOException

async def request_validation_exception_handler_422(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    捕捉422报错并进行自定义处理
    :param request:
    :param exc:
    :return:
    """
    array = []
    for item in exc.errors():
        msg = item['msg']
        field = item['loc'][-1]

        if item['type']=="value_error.missing" and msg=='field required':
            msg = '字段不能为空'
        elif item['type']=='value_error.jsondecode':
            msg = "参数格式错误"
            field = ""

        array.append({
            'field': field,
            'msg': msg

        })

    status_code = 200
    return JSONResponse(
        status_code=status_code,
        content={
            "code": 422,
            "msg": "",
            "data": {
                "detail": array,
                "debug": exc.errors()
            }
        },
    )

async def request_ssoexception_handler(request: Request, exc: SSOException) -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content=exc.output(),
    )