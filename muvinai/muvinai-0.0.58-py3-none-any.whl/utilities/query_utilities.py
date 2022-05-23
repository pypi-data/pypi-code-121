from flask import request, jsonify, make_response


def filterQuery(model):
    queryDict = eval(request.args.get('filter'))
    sociosFiltered = model(__raw__=queryDict)
    if len(sociosFiltered) == 0:
        sociosFiltered = 'no result found'
        resp = make_response({'data': {sociosFiltered}})
        resp.headers['Content-Range'] = f"testing"
        return resp