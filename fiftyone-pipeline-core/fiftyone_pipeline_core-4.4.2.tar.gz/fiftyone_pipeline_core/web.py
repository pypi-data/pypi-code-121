# *********************************************************************
# This Original Work is copyright of 51 Degrees Mobile Experts Limited.
# Copyright 2022 51 Degrees Mobile Experts Limited, Davidson House,
# Forbury Square, Reading, Berkshire, United Kingdom RG1 3EU.
#
# This Original Work is licensed under the European Union Public Licence
# (EUPL) v.1.2 and is subject to its terms as set out below.
#
# If a copy of the EUPL was not distributed with this file, You can obtain
# one at https://opensource.org/licenses/EUPL-1.2.
#
# The 'Compatible Licences' set out in the Appendix to the EUPL (as may be
# amended by the European Commission) shall be deemed incompatible for
# the purposes of the Work and the provisions of the compatibility
# clause in Article 5 of the EUPL shall not apply.
# 
# If using the Work as, or as part of, a network application, by 
# including the attribution notice(s) required under Article 5 of the EUPL
# in the end user terms of the application under an appropriate heading, 
# such notice(s) shall fulfill the requirements of that article.
# ********************************************************************* 

from flask import request

def webevidence(request):

    """!
    Get evidence from a web request (gets headers, cookies and query parameters)
    
    @type request: Request 
    @param request: A Request object
    @rtype dict
    @return A dictionary of web evidence that can be using in flowdata.evidence.add_from_dict()

    """

    webevidence = {}

    for header in request.headers:
        webevidence["header." + header[0].lower()] = header[1]

    for cookieKey, cookieValue in request.cookies.items():
        webevidence["cookie." + cookieKey] = cookieValue

    for query,value in request.args.items():

        webevidence["query." + query] = value
    
    webevidence["server.client-ip"] =  request.remote_addr

    webevidence["server.host-ip"] =  request.host

    if (request.is_secure):
        webevidence["header.protocol"] = "https"
    else:
        webevidence["header.protocol"] = "http"

    return webevidence

def set_response_header(flowData, response):
    
    """!
    Set UACH response header in web response (sets Accept-CH header in response)
    
    @type response: Response 
    @param response: A Response object
    @param response_header_dict: Dictionary containing response header key and values to be set
    @rtype response
    @return A response object containing headers with non null values in response

    """
    
    # Get response headers dictionary containing key values to be set in response  
    response_header_dict = flowData["set-headers"]["responseheaderdictionary"]
    for response_key, response_value in response_header_dict.items():
        response_value = response_value.replace(",", ", ")
        if response_value != "":
            response.headers[response_key] = response_value

    return response