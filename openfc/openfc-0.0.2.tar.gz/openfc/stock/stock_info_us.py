import pandas as pd
import requests
import json
from openfc import db
from py_mini_racer import py_mini_racer

us_sina_stock_list_url = "http://stock.finance.sina.com.cn/usstock/api/jsonp.php/IO.XSRV2.CallbackList[{}]/US_CategoryService.getList"
us_sina_stock_dict_payload = {
    "page": "2",
    "num": "20",
    "sort": "",
    "asc": "0",
    "market": "",
    "id": ""
}

js_hash_text = """
    function d(s){
		var a, i, j, c, c0, c1, c2, r;
		var _s = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_$';
		var _r64 = function(s, b)
		{
			return ((s | (s << 6)) >>> (b % 6)) & 63;
		};
		a = [];
		c = [];
		for (i = 0; i < s.length; i++)
		{
			c0 = s.charCodeAt(i);
			if (c0 & ~255)
			{
				c0 = (c0 >> 8) ^ c0;
			}
			c.push(c0);
			if (c.length == 3 || i == s.length - 1)
			{
				while(c.length < 3)
				{
					c.push(0);
				}
				a.push((c[0] >> 2) & 63);
				a.push(((c[1] >> 4) | (c[0] << 6)) & 63);
				a.push(((c[1] << 4) | (c[2] >> 2)) & 63);
				a.push(c[2] & 63);
				c = [];
			}
		}
		while (a.length < 16)
		{
			a.push(0);
		}
		r = 0;
		for (i = 0; i < a.length; i++)
		{
			r ^= (_r64(a[i] ^ (r | i), i) ^ _r64(i, r)) & 63;
		}
		for (i = 0; i < a.length; i++)
		{
			a[i] = (_r64((r | i & a[i]), r) ^ a[i]) & 63;
			r += a[i];
		}
		for (i = 16; i < a.length; i++)
		{
			a[i % 16] ^= (a[i] + (i >>> 4)) & 63;
		}
		for (i = 0; i < 16; i++)
		{
			a[i] = _s.substr(a[i], 1);
		}
		a = a.slice(0, 16).join('');
		return a;
	}
"""


def stock_info_us_list() -> pd.DataFrame:
    """
    u.s. stock's english name, chinese name and symbol
    you should use symbol to get apply into the next function
    http://finance.sina.com.cn/stock/usstock/sector.shtml
    :return: stock's english name, chinese name and symbol
    :rtype: pandas.DataFrame
    """
    import time
    last_update_time, df = db.db_load('stock_info_us_list')

    if time.time() - last_update_time > 60 * 60 * 24:
        page_count = get_us_page_count()
        df = pd.DataFrame()
        for page in range(1, page_count + 1):
            # page = "1"
            print('stock_info_us_list', page)
            us_js_decode = "US_CategoryService.getList?page={}&num=20&sort=&asc=0&market=&id=".format(
                page)
            js_code = py_mini_racer.MiniRacer()
            js_code.eval(js_hash_text)
            dict_list = js_code.call("d", us_js_decode)  # 执行js解密代码
            us_sina_stock_dict_payload.update({"page": "{}".format(page)})
            res = requests.get(us_sina_stock_list_url.format(dict_list),
                               params=us_sina_stock_dict_payload)
            data_json = json.loads(res.text[res.text.find("({") +
                                            1:res.text.rfind(");")])
            df = df.append(pd.DataFrame(data_json["data"]), ignore_index=True)
        save_to_db('stock_info_us_list', df)
    else:
        print("stock_info_us_list load form db, last update time = {}".format(
            last_update_time))
    return df[["name", "cname", "symbol"]]


def get_us_page_count() -> int:
    """
    新浪财经-美股-总页数
    http://finance.sina.com.cn/stock/usstock/sector.shtml
    :return: 美股总页数
    :rtype: int
    """
    page = "1"
    us_js_decode = f"US_CategoryService.getList?page={page}&num=20&sort=&asc=0&market=&id="
    js_code = py_mini_racer.MiniRacer()
    js_code.eval(js_hash_text)
    dict_list = js_code.call("d", us_js_decode)  # 执行js解密代码
    us_sina_stock_dict_payload.update({"page": "{}".format(page)})
    res = requests.get(us_sina_stock_list_url.format(dict_list),
                       params=us_sina_stock_dict_payload)
    data_json = json.loads(res.text[res.text.find("({") +
                                    1:res.text.rfind(");")])
    if not isinstance(int(data_json["count"]) / 20, int):
        page_count = int(int(data_json["count"]) / 20) + 1
    else:
        page_count = int(int(data_json["count"]) / 20)
    return page_count


def save_to_db(tag: str, df: pd.DataFrame):
    db.db_save(tag, df)
