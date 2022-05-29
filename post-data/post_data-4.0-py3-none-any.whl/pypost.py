from requests import get,post
from kamabayEncoder import KAMABAY_ENCODE_DECODE

ua = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'}
enc = """$dsew[KMY]p56da[KMY]p56da[KMY]dfe12[KMY]edwqe[KMY]havxa[KMY]fwstg[KMY]fwstg[KMY]dfe12[KMY]u`u!y[KMY]dfe12[KMY]p039=[KMY]edwqe[KMY]p56da[KMY]ad/?s[KMY]dfe12[KMY]u`u!y[KMY]p56da[KMY]$dsew[KMY]p039=[KMY]gereg[KMY]!@$#%[KMY]gereg[KMY]u`u!y[KMY]^'-hd[KMY]$dsew[KMY]fgdgf[KMY]3sdfh[KMY]fgdgf[KMY]ad/?s[KMY]!@#$%[KMY]p039=[KMY]vuvue[KMY]fwstg[KMY]!@$#%[KMY]dfe12[KMY]feswe[KMY]fwstg[KMY]"""

def get_data(key) -> str:
    'your data key';
    if not key:
        return 'Error key!';
    else:
        req = get(
            url=KAMABAY_ENCODE_DECODE(enc,False).decode(),
            params={'keys':key},headers=ua);
        if req.status_code == 200:
            str = "";
            try:
                for i,dt in enumerate(req.json()['data']):
                    db = f'{i+1} - {dt["data"]} -> {dt["timezone"][:10]}\n'
                    str += db;
                return str;
            except:
                return 'Error data!'
        else:
            return f'Error code {req.status_code}'

def post_data(key,**data):
    "the keyword 'keys' for your data security is mandatory."
    if not key:
        return f'Error keys!\ncreate a security lock to protect your data!'
    else:
        data['keys'] = key;
        url = KAMABAY_ENCODE_DECODE(enc,False).decode()
        post_dt = post(url,data=data,headers=ua);
        if post_dt.status_code == 200:
            return f"\t{post_dt.text}\n\nurl : https://pypost.pythonanywhere.com/ - key : {key}"
        else:return f'Error code {post_dt.status_code}'
