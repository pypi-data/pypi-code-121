from flask import request


# token = request.args.get('token')
# print(token)
#

def login_required(func):
    token = request.args.get('token')
    print("login_reuired token is {}".format(token))

    # @wrap
    def login_required_wraper(*args, **kwargs):
        if request.args.get('token'):

            # post_req = Rest(f'http://{Constants.GATEWAY_SERVER_IP}:{Constants.GATEWAY_PORT}',
            #                 path='/sdk/offline/get',
            #                 header={'Content-Type': 'application/json; charset=utf-8', 'token': token})
            # response = post_req.post()
            response = "<Response [200]>"
            if response is "<Response [200]>":
                func()
            # return "you are not loggin"
        return "you are not loggin"
    return login_required_wraper
