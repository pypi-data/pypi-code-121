from hbshare.db.ApiCfg import UrlEnum
# from ApiCfg import UrlEnum
from hbshare.base.data_pro import hb_api
# import hbshare as hbs
import pandas as pd
import time

def fieldsCheckd(kwargs,supportFields: tuple):
    fields = kwargs.get('fields') 
    if fields is None or len(fields) == 0:
        # 元组转list
        kwargs['fields'] = list(supportFields)
        return
    for field in fields:
        if field not in supportFields:
            raise ValueError("field %s not supported" % field)


def commonQuery(urlEnum, pause=0.01, timeout=10,**kwargs):
    '''
        通用Api调用方法
        :param urlEnum: 指定API枚举
        :param fields: 限定查询结果列,可选,默认使用API配置的所有字段
        :return: 以fields为列的dataframe
    '''
    if urlEnum is None:
        raise ValueError("必须指定接口配置")
    if type(urlEnum) is str:
        cfg = UrlEnum.getValue(urlEnum)
    else:
        cfg = urlEnum.value
    if kwargs is None:
        kwargs = {}
    # 判断目标字段是否指定，没指定则使用接口支持字段
    fieldsCheckd(kwargs,cfg.supportFields)
    api = hb_api(timeout=timeout)
    pages = 1
    page = 1
    perPage = 1000
    data = []
    while page <= pages:
        kwargs['page'] = page
        kwargs['perPage']= perPage
        try:
            # json传参
            post_data = cfg.parsePostData(kwargs)
            # url链接后拼接
            params = cfg.parseParams(kwargs)
        except KeyError as e:
            raise RuntimeError("Use commonQuery(%s) failed,parameter %s not found" % (urlEnum,e.args[0]))

        org_js = api.query(cfg.getUrl(), method=cfg.method, params=params,post_data=post_data)
        status_code = str(org_js['code'])
        if status_code != '0000':
            status = str(org_js['desc'])
            raise ValueError(status)
        if 'body' not in org_js:
            status = "未查询到估值信息"
            raise ValueError(status)
        body = org_js['body']
        if type(body) is list:
            # 接口不分页
            data += org_js['body']
            continue
        if 'records' in body and 'pages' in body:
            # 总页数  
            pages = body['pages']
            # 页码加1
            page += 1
            data += body['records']
            time.sleep(pause)
            continue
        # 返回的是单个对象
        data.append(body)
    prod_df = pd.DataFrame(data,columns = kwargs['fields'])
    return prod_df


if __name__ == '__main__':

    data = commonQuery('SC_VALUATION_A', startDate ='2019-07-22 00:00:00', endDate='2019-07-22 00:00:00')
    print(data)
