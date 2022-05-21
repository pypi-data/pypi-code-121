# import logging

# from cgcomponents import const
# from cgcomponents.requests_cg import post_cg

# logging.basicConfig(filename='logsPortal.log', level=logging.INFO,
#                     format='%(levelname)s - %(message)s')


# def LogsMicroService(mc):
#     json = {'microservice': mc}

#     logging.info(mc)

#     post_cg(const.URL_API_MICROSERVICE, json)


# def LogsInfo(messages):

#     json = {
#         "info_message": [
#             {
#                 "messages": messages
#             }
#         ]
#     }
#     post_cg(const.URL_API_INFOS, json)

#     logging.info(messages)
#     pass


# def LogsErros(erros):

#     json = {
#         #"traceback": traceback,
#         "error_mesage": erros
#     }
#     post_cg(const.URL_API_ERROS, json)

#     logging.error(erros)
#     pass


# def LogsCriticalErros(critical):

#     json = {
#             "critical": critical
#     }
#     post_cg(const.URL_API_CRITICALS, json)

#     logging.warning(critical)
#     pass


# def LogsSuccess(success):

#     json = {
#         "success_mesage": success
#     }
#     post_cg(const.URL_API_SUCCESS, json)

#     logging.info(success)
#     pass