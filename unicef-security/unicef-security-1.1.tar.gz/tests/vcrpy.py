import vcr

VCR = vcr.VCR(serializer='yaml',
              record_mode='once',
              match_on=['uri', 'method'],
              filter_headers=['authorization', 'token'],
              filter_post_data_parameters=['client_id', 'client_secret'],
              decode_compressed_response=True)


# def _getvcr(request, env):
#     if env in os.environ:
#         params = {'record_mode': 'all'}
#         # params = {'record_mode': 'new_episodes'}
#     else:
#         params = {'record_mode': 'none'}
#     path = str(Path(request.fspath).parent / 'cassettes' / str(request.function.__name__))
#     return VCR(cassette_library_dir=path,
#                filter_headers=['authorization', 'token'],
#                filter_post_data_parameters=['client_id', 'client_secret'],
#                filter_query_parameters=['access_key'],
#                **params)
