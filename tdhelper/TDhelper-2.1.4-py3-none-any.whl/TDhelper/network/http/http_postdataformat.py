import json
import random
import hashlib


def xWwwFormUrlencoded(v: dict, encoding='utf-8', headers: dict = None):
    '''
        if http post content-type is application/x-www-form-urlencoded, then you can use this function to translate post data chunk.

        params:
        - v: <dict>. your post data, value formatter(n1=x1&n2=x2...).
        - encoding: <str>. encoding type, default value is utf-8.  

        returns:
        - headers:<dict>. http header.
        - data: <str>. post data string.
    '''
    try:
        m_v = ''
        count = 0
        for k, k_v in v.items():
            m_v += k+"="+k_v
            count += 1
            if count < len(v):
                m_v += "&"
        if headers:
            headers["Content-type"] = "application/x-www-form-urlencoded; charset= %s" % encoding
        else:
            headers = {
                "Content-Type": "application/x-www-form-urlencoded; charset= %s" % encoding}
        data = m_v.replace("+", "%2B")
        data = data.encode(encoding)
        return headers, data
    except Exception as e:
        raise e


def formData(v: dict, encoding='utf-8', headers: dict = None):
    '''
        if http post content-type is multipart/form-data, then you can use this function to translate post data chunk.

        params:
        - v: <dict>. your post data.
        - encoding: <str>. encoding type, default value is utf-8.

        returns:
        - header: <dict>. 
        - data: <json> 
    '''
    try:
        token = str(random.randint(0, 100000))
        m_md5 = hashlib.md5()
        m_md5.update(token.encode(encoding))
        token = m_md5.hexdigest()
        boundaryStr = "----WebKitFormBoundary%s" % token
        if headers:
            headers["Content-type"] = "multipart/form-data; boundary=%s" % boundaryStr
            headers["cache-control"] = "no-cache"
        else:
            headers = {
                'Content-Type': "multipart/form-data; boundary=%s" % boundaryStr,
                'cache-control': "no-cache",
            }
        startStr = '--'+boundaryStr+'\r\n'
        dataDispositionFormatter = "Content-Disposition: form-data; name=\"{0}\"\r\n\r\n{1}\r\n"
        endStr = '--'+boundaryStr+'--'
        data = ''
        if isinstance(v, dict):
            for item, value in v.items():
                data += dataDispositionFormatter.format(item, value)
            data = startStr + data + endStr
            return headers, data
        else:
            raise Exception("parameter 'v' type must is dict.")
    except Exception as e:
        raise e


def jsonData(v: dict, encoding: str = 'utf-8', headers: dict = None):
    '''
        if http post content-type is application/json, then you can use this function to translate post data chunk.

        params:
        - v: <dict>. your post data.
        - encoding: <str>. encoding type, default value is utf-8.

        returns:
        - header: <dict>. 
        - data: <json> 
    '''
    try:
        if headers:
            headers["Content-Type"] = "application/json;charset=%s" % encoding
        else:
            headers = {"Content-Type": "application/json;charset=%s" % encoding}
        return headers, json.dumps(v)
    except json.JSONDecodeError as e:
        raise e


def xmlData(v: dict, encoding: str = 'utf-8'):
    '''
        wait for, void function.
    '''
    pass


if __name__ == '__main__':
    dictData = {'name': 'tangjing', 'pwd': '123456'}
    strData = "name=tangjing&pwd=123456"

    header, data = xWwwFormUrlencoded(dictData)
    print(header)
    print(data)
