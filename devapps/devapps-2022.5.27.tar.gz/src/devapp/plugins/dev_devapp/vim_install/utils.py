import json, requests
from devapp.app import FLG


def vim_infos(api_nvim):
    def clean(rel):
        ass = rel.pop('assets')
        ai = [k for k in ass if k['name'].endswith('.appimage')][0]
        ai = {k: ai[k] for k in ['size', 'updated_at', 'browser_download_url']}
        rel['appimg'] = ai
        #rel.pop('author', 0)
        #rel.pop('reactions', 0)
        f = '### Features'
        b = rel.pop('body', '').split(f, 1)
        if len(b) == 1:
            f = ''
        else:
            f = b[1].split('\n### ', 1)[0]
        f = [i.split('([', 1)[0] for i in f.split('\r\n') if i]
        rel = {k: rel[k] for k in ['appimg', 'tag_name', 'html_url']}
        if f:
            rel['features'] = f
        return rel

    r = requests.get(api_nvim)
    r = json.loads(r.text)
    rr = []
    while r:
        rr.append(r.pop(0))
        if rr[-1]['tag_name'] == FLG.nvim_version:
            break
    r = [clean(rel) for rel in rr]
    r = {i.pop('tag_name'): i for i in r}
    return r
