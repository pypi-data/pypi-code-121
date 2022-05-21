import os, requests, json, sys
from pathlib import Path
from getpass import getpass
from typing import Optional

from pydantic import BaseModel

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

import filetype

class ClientConfig(BaseModel):
    base_url: str
    balaio: Optional[str] = None
    mucua: Optional[str] = None
    username: Optional[str] = None

class BaobaxiaClient():
    
    def __init__(self, config_file=None):
        super().__init__()
        if config_file is None:
            self.config_file = Path.home() / '.baobaxia' / 'client.config'
        else:
            if not isinstance(config_file, Path):
                config_file = Path(config_file)
            self.config_file = config_file
        if self.config_file.exists():
            self.load_config()
        else:
            url = input('URL: ')
            self.config = ClientConfig(base_url = url)
        self.session = None
        self.last_response = None

    def load_config(self):
        self.config = ClientConfig.parse_file(
            self.config_file)
        
    def save_config(self):
        self.config_file.open('w').write(
            self.config.json())

    def get_headers(self):
        result = {}
        if self.session is not None:
            if isinstance(self.session, dict):
                result['token'] = self.session['token']
            else:
                result['token'] = self.session.token
        return result
    
    def request(self, method, path,
                data=None,
                files=None,
                as_json=True,
                pretty_print=True,
                use_balaio=True,
                use_mucua=True
    ):
        method = method.lower()
        if method == 'del':
            method = 'delete'
        url = self.config.base_url
        if use_balaio:
            url = url + self.config.balaio + '/'
            if use_mucua:
                url = url + self.config.mucua + '/'
        url = url + path
        print('URL: ' + url)
        self.last_response = getattr(requests, method)(
            url,
            data = data,
            files = files,
            headers = self.get_headers())
        if as_json and pretty_print:
            json_str = json.dumps(self.last_response.json(),
                                  sort_keys=True,
                                  indent=2,
                                  separators=(',', ': '))
            return highlight(json_str, JsonLexer(), TerminalFormatter())
        if as_json:
            return self.last_response.json()
        return self.last_response.content
    
    def auth(self):
        password = getpass('Senha: ')
        self.session = self.request('post',
            'auth',
            data={'username': self.config.username, 'password': password},
            pretty_print=False
            )
        return self.session
    
    def list_balaios(self, pretty_print=True):
        if pretty_print:
            print(self.request('get', 'balaio', use_balaio=False))
        else:
            return self.request('get', 'balaio', pretty_print=False, use_balaio=False)
    
    def post_balaio(self, name, default_mucua):
        print(self.request('post', 'balaio',
            data={'name': name, 'default_mucua': default_mucua},
            use_balaio=False))
    
    def get_balaio(self, balaio, pretty_print=True):
        if pretty_print:
            print(self.request('get', 'balaio/'+balaio, use_balaio=False))
        else:
            return self.request('get', 'balaio/'+balaio, pretty_print=False, use_balaio=False)
    
    def put_balaio(self, balaio, name, default_mucua):
        print(self.request('put', 'balaio/'+balaio,
            data={'name': name, 'default_mucua': default_mucua}, use_balaio=False))
    
    def del_balaio(self, balaio):
        print(self.request('del', 'balaio/'+balaio, use_balaio=False))
    
    def list_mucuas(self, pretty_print=True):
        if pretty_print:
            print(self.request('get', 'mucua', use_mucua=False))
        else:
            return self.request('get', 'mucua',
                                pretty_print=False, use_mucua=False)
    
    def post_mucua(self, name):
        print(self.request('post', 'mucua',
            data={'name': name}, use_mucua=False))
    
    def get_mucua(self, mucua, pretty_print=True):
        if pretty_print:
            print(self.request('get', 'mucua/'+mucua, use_mucua=False))
        else:
            return self.request('get', 'mucua/'+mucua,
                                pretty_print=False, use_mucua=False)
    
    def put_mucua(self, mucua, name):
        print(self.request('put', 'mucua/'+mucua,
            data={'name': name}, use_mucua=False))
    
    def del_mucua(self, mucua):
        print(self.request('del', 'mucua/'+mucua, use_mucua=False))
    
    def list_mocambolas(self, pretty_print=True):
        if pretty_print:
            print(self.request('get', 'mocambola'))
        else:
            return self.request('get', 'mocambola', pretty_print=False)
    
    def get_mocambola(self, username, pretty_print=True):
        if pretty_print:
            print(self.request('get', 'mocambola/'+username))
        else:
            return self.request('get', 'mocambola/'+username, pretty_print=False)
    
    def post_mocambola(self, mocambola):
        print(self.request('post', 'mocambola',
                           data=json.dumps(mocambola)))
    
    def put_mocambola(self, username, mocambola):
        print(self.request('put', 'mocambola/'+username,
                           data=json.dumps(mocambola)))
    
    def del_mocambola(self, username):
        print(self.request('del', 'mocambola/'+username))
    
    def list_midias(self, pretty_print=True):
        if pretty_print:
            print(self.request('get', 'acervo/midia'))
        else:
            return self.request('get', 'acervo/midia', pretty_print=False)
    
    def get_midia(self, path, pretty_print=True):
        if pretty_print:
            print(self.request('get', 'acervo/midia/'+str(path)))
        else:
            return self.request('get', 'acervo/midia/'+str(path), pretty_print=False)
    
    def post_midia(self, titulo, descricao, autor, mocambo, tipo, tags):
        print(self.request('post', 'acervo/midia',
            data={
                'titulo': titulo,
                'descricao': descricao,
                'autor': autor,
                'mocambo': mocambo,
                'tipo': tipo,
                'tags': tags
            }))
    
    def put_midia(self, path, titulo, descricao, autor, mocambo, tags):
        print(self.request('put', 'acervo/midia/'+str(path),
            data={
                'titulo': titulo,
                'descricao': descricao,
                'autor': autor,
                'mocabo': mocambo,
                'tags': tags
            }))
    
    def del_midia(self, path):
        print(self.request('del', 'acervo/midia/'+str(path)))
    
    def upload_midia(self, path, arquivo):
        name = os.path.basename(arquivo)
        with open(arquivo, 'rb') as f:
            print(self.request('post',
                'acervo/upload/'+str(path),
                as_json=False,
                files={'arquivo': (name,f)}))
    
    def download_midia(self, path, arquivo):
        content = self.request('get', 'acervo/download/'+str(path), as_json=False)
        with open(arquivo, 'wb') as f:
            f.write(content)

    def download_thumbnail(self, path, arquivo):
        content = self.request('get', 'acervo/thumbnail/'+str(path), as_json=False)
        with open(arquivo, 'wb') as f:
            f.write(content)
    
    def publish_midia(self, path):
        return self.request('put', 'acervo/publish/'+str(path))
    
    def find_midias(self, keywords=None,
                    hashtags=None, tipos=None,
                    status=None, creator=None,
                    ordem_campo=None, ordem_decrescente=None,
                    pag_tamanho=None, pag_atual=None,
                    pretty_print=True):
        url = 'acervo/find?'
        if keywords is not None:
            url += 'keywords='+keywords+'&'
        if hashtags is not None:
            url += 'hashtags='+hashtags+'&'
        if tipos is not None:
            url += 'tipos='+tipos+'&'
        if status is not None:
            url += 'status='+status+'&'
        if creator is not None:
            url += 'creator='+creator+'&'
        if ordem_campo is not None:
            url += 'ordem_campo='+ordem_campo+'&'
        if ordem_decrescente is not None:
            url += 'ordem_decrescente='+str(ordem_decrescente)+'&'
        if pag_tamanho is not None:
            url += 'pag_tamanho='+str(pag_tamanho)+'&'
        if pag_atual is not None:
            url += 'pag_atual='+str(pag_atual)+'&'
        if pretty_print:
            print(self.request('get', url))
        else:
            return self.request('get', url)
    
    def get_tipos_por_content_type(self):
        return self.request('get', 'acervo/tipos_por_content_type')
        
    def get_top_tags(self, size=None):
        url = 'acervo/top_tags'
        if size is not None:
            url = url + '?size=' + str(size)
        return self.request('get', url)

    def upload_dir(self, input_dir, output_dir, types=None):
        if types is None:
            self.request('get', 'acervo/tipos_por_content_type')
            types = self.last_response.json()
        files = os.listdir(input_dir)
        for f in files:
            in_file = input_dir / f
            out_file = output_dir / f
            
            print("**** " + str(in_file) + " ****")
            
            if in_file.is_dir():
                if not out_file.exists():
                    out_file.mkdir()
                self.upload_dir(in_file, out_file, types)
                in_file.rmdir()
            else:
                a_type = filetype.guess(in_file)
                tipo = None
                if a_type is None:
                    tipo = 'arquivo'
                elif a_type.mime[0:5] == 'image':
                    tipo = 'imagem'
                elif a_type.mime[0:5] == 'video':
                    tipo = 'video'
                elif a_type.mime[0:5] == 'audio':
                    tipo = 'audio'
                else:
                    tipo = 'arquivo'
                midia = self.request('post', 'acervo/midia',
                    data={
                        'titulo': f,
                        'descricao': f,
                        'autor': 'Migração',
                        'mocambo': 'Instituto Janeraka',
                        'tipo': tipo,
                        'tags': ''
                    },
                    pretty_print=False)
                assert self.last_response.status_code == 200
                
                with open(in_file, 'rb') as file_data:
                    self.request('post',
                        'acervo/upload/'+str(midia['path']),
                        pretty_print=False,
                        files={'arquivo': (f,file_data)})
                assert self.last_response.status_code == 200
                
                in_file.rename(out_file)
