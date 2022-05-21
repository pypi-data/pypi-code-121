from pathlib import Path
from typing import Optional, List, Any
import traceback

from fastapi import FastAPI, Header, Form, HTTPException

from pydantic import BaseModel, Field

from .saberes import (
    Saber,
    SaberesConfig,
    Balaio,
    Mucua,
    Mocambola
)
from .sankofa import Sankofa
from .root import (
    Baobaxia,
    BaobaxiaError,
    SessionNotFound,
    SessionExpired
)

from configparser import ConfigParser

ROLE_MUCUA_PAJE = "mucua.paje"


class BaobaxiaAPI(FastAPI):

    def __init__(
            self,
            config: Optional[SaberesConfig] = None,
            prefix: Optional[str] = None,
            tags: Optional[List[str]] = None,
            root_path: str = "",
            **kwargs: Any) -> None:
        super().__init__(prefix=prefix,
                         tags=tags, root_path=root_path, **kwargs)
        self.baobaxia = Baobaxia()

        super().add_api_route(
            '/auth',
            self.authenticate,
            methods=['POST'],
            response_model=dict,
            summary='Autenticar mocambola')
        super().add_api_route(
            '/keepalive',
            self.keep_alive,
            methods=['GET'],
            summary='Mantém ativa a sessão do mocambola')
        super().add_api_route(
            '/recover',
            self.recover,
            methods=['POST'],
            response_model=str,
            summary='Recuperar mocambola')
        super().add_api_route(
            '/balaio',
            self.list_balaios,
            methods=['GET'],
            response_model=List[Balaio],
            summary='Listar balaios')
        super().add_api_route(
            '/balaio',
            self.post_balaio,
            methods=['POST'],
            response_model=Balaio,
            summary='Criar um novo balaio')
        super().add_api_route(
            '/balaio/{balaio_slug_smid}',
            self.get_balaio,
            methods=['GET'],
            response_model=Balaio,
            summary='Retornar um balaio')
        super().add_api_route(
            '/balaio/{balaio_slug_smid}',
            self.put_balaio,
            methods=['PUT'],
            response_model=Balaio,
            summary='Atualizar um balaio')
        super().add_api_route(
            '/balaio/{balaio_slug_smid}',
            self.del_balaio,
            methods=['DELETE'],
            summary='Deletar um balaio')
        
        super().add_api_route(
            '/{balaio_slug_smid}/mucua',
            self.list_mucuas,
            methods=['GET'],
            response_model=List[Mucua],
            summary='Listar mucuas')
        super().add_api_route(
            '/{balaio_slug_smid}/mucua',
            self.post_mucua,
            methods=['POST'],
            response_model=Mucua,
            summary='Criar uma nova mucua')
        super().add_api_route(
            '/{balaio_slug_smid}/mucua/{mucua_slug_smid}',
            self.get_mucua,
            methods=['GET'],
            response_model=Mucua,
            summary='Retornar uma mucua')
        super().add_api_route(
            '/{balaio_slug_smid}/mucua/{mucua_slug_smid}',
            self.put_mucua,
            methods=['PUT'],
            response_model=Mucua,
            summary='Atualizar uma mucua')
        super().add_api_route(
            '/{balaio_slug_smid}/mucua/{mucua_slug_smid}',
            self.del_mucua,
            methods=['DELETE'],
            summary='Deletar uma mucua')

        '''
        super().add_api_route(
            '/mucua/{balaio_slug}/{mucua_slug}/remote',
            self.mucua_remote_get,
            methods=['GET'],
            summary='Retornar os remotes da mucua')
        super().add_api_route(
            '/mucua/{balaio_slug}/{mucua_slug}/remote',
            self.mucua_remote_add,
            methods=['POST'],
            summary='Adicionar um remote na mucua')
        super().add_api_route(
            '/mucua/{balaio_slug}/{mucua_slug}/remote',
            self.mucua_remote_del,
            methods=['DELETE'],
            summary='Remover um remote da mucua')

        super().add_api_route(
            '/mucua/{balaio_slug}/{mucua_slug}/group',
            self.mucua_group_list,
            methods=['GET'],
            summary='Retornar os grupos da mucua')
        super().add_api_route(
            '/mucua/{balaio_slug}/{mucua_slug}/group',
            self.mucua_group_add,
            methods=['POST'],
            summary='Adicionar um grupo na mucua')
        super().add_api_route(
            '/mucua/{balaio_slug}/{mucua_slug}/group',
            self.mucua_group_del,
            methods=['DELETE'],
            summary='Remover um grupo da mucua')
        '''

        super().add_api_route(
            '/{balaio_slug_smid}/{mucua_slug_smid}/mocambola',
            self.list_mocambolas,
            methods=['GET'],
            response_model=List[Mocambola],
            summary='Listar mocambolas')
        super().add_api_route(
            '/{balaio_slug_smid}/{mucua_slug_smid}/mocambola',
            self.post_mocambola,
            methods=['POST'],
            response_model=Mocambola,
            summary='Criar um novo mocambola')
        super().add_api_route(
            '/{balaio_slug_smid}/{mucua_slug_smid}/mocambola/{username}',
            self.get_mocambola,
            methods=['GET'],
            response_model=Mocambola,
            summary='Retornar um mocambola')
        super().add_api_route(
            '/{balaio_slug_smid}/{mucua_slug_smid}/mocambola/{username}',
            self.put_mocambola,
            methods=['PUT'],
            response_model=Mocambola,
            summary='Atualizar um mocambola')
        super().add_api_route(
            '/{balaio_slug_smid}/{mucua_slug_smid}/mocambola/{username}',
            self.del_mocambola,
            methods=['DELETE'],
            summary='Deletar um mocambola')
        super().add_api_route(
            '/{balaio_slug_smid}/{mucua_slug_smid}/mocambola/add_balaio',
            self.add_mocambola_balaio,
            methods=['POST'],
            summary='Adicionar mocambola no balaio')
        super().add_api_route(
            '/{balaio_slug_smid}/{mucua_slug_smid}/mocambola/password',
            self.set_password,
            methods=['POST'],
            summary='Atualiza a senha do mocambola autenticado')

    def extract_smid(self, slug_smid: str):
        return slug_smid[-self.baobaxia.config.smid_len:]
        
    def add_saberes_api(self, model: type, **kwargs):
        if 'field_name' in kwargs and kwargs['field_name'] is not None:
            field_name = kwargs['field_name']
        else:
            field_name = model.__name__.lower()
        if 'list_field_name' in kwargs and kwargs[
                'list_field_name'] is not None:
            list_field_name = kwargs['list_field_name']
        else:
            list_field_name = field_name + 's'

        if 'url_path' in kwargs:
            url_path = '/{balaio_slug_smid}/{mucua_slug_smid}/'+kwargs[
                'url_path']
        else:
            url_path = '/{balaio_slug_smid}/{mucua_slug_smid}/'+field_name

        if 'list_summary' in kwargs:
            summary = kwargs['list_summary']
        else:
            summary = 'Listar '+list_field_name
        if 'list_url' in kwargs:
            list_url = kwargs['list_url']
        else:
            list_url = url_path
        if 'list_method' in kwargs and callable(kwargs['list_method']):
            super().add_api_route(
                list_url,
                kwargs['list_method'],
                response_model=List[model],
                methods=['GET'],
                summary=summary)
        elif 'skip_list_method' not in kwargs:
            def list_rest_template(*,
                                   balaio_smid: str,
                                   mucua_smid: str,
                                   token: Optional[str] = Header(None)):
                try:
                    return getattr(self.baobaxia, 'list_'+list_field_name)(
                        balaio_smid, mucua_smid, token)
                except (SessionNotFound, SessionExpired):
                    traceback.print_exc()
                    raise HTTPException(status_code=401, detail="Token inválido")
                except Exception as e:
                    traceback.print_exc()
                    raise HTTPException(status_code=500, detail=str(e))

            super().add_api_route(
                list_url,
                list_rest_template,
                response_model=List[model],
                methods=['GET'],
                summary=summary)

        if 'get_summary' in kwargs:
            summary = kwargs['get_summary']
        else:
            summary = 'Retornar '+field_name
        if 'get_url' in kwargs:
            get_url = kwargs['get_url']
        else:
            get_url = '/'+url_path+'/{slug_smid:str}'
        if 'get_method' in kwargs and callable(kwargs['get_method']):
            super().add_api_route(
                get_url,
                kwargs['get_method'],
                response_model=model,
                methods=['GET'],
                summary=summary)
        elif 'skip_get_method' not in kwargs:
            def get_rest_template(*,
                                  balaio_slug_smid: str,
                                  mucua_slug_smid: str,
                                  slug_smid: str,
                                  token: Optional[str] = Header(None)):
                try:
                    balaio_smid = self.extract_smid(balaio_slug_smid)
                    mucua_smid = self.extract_smid(mucua_slug_smid)
                    smid = self.extract_smid(slug_smid)
                    return getattr(self.baobaxia, 'get_'+field_name)(
                        balaio_smid, mucua_smid, smid, token)
                except (SessionNotFound, SessionExpired):
                    traceback.print_exc()
                    raise HTTPException(status_code=401, detail="Token inválido")
                except Exception as e:
                    traceback.print_exc()
                    raise HTTPException(status_code=500, detail=str(e))

            super().add_api_route(
                get_url,
                get_rest_template,
                response_model=model,
                methods=['GET'],
                summary=summary)

        if 'put_summary' in kwargs:
            summary = kwargs['put_summary']
        else:
            summary = 'Atualizar '+field_name
        if 'put_url' in kwargs:
            put_url = kwargs['put_url']
        else:
            put_url = url_path
        if 'put_method' in kwargs and callable(kwargs['put_method']):
            super().add_api_route(
                put_url,
                kwargs['put_method'],
                response_model=model,
                methods=['PUT'],
                summary=summary)
        elif 'skip_put_method' not in kwargs:
            def put_rest_template(*,
                                  balaio_slug_smid: str,
                                  mucua_slug_smid: str,
                                  slug_smid: str,
                                  data: model,
                                  token: str = Header(...)):
                try:
                    balaio_smid = self.extract_smid(balaio_slug_smid)
                    mucua_smid = self.extract_smid(mucua_slug_smid)
                    smid = self.extract_smid(slug_smid)
                    assert smid == data.smid
                    return getattr(self.baobaxia, 'put_'+field_name)(
                        balaio_smid, mucua_smid, smid, data, token)
                except (SessionNotFound, SessionExpired):
                    traceback.print_exc()
                    raise HTTPException(status_code=401, detail="Token inválido")
                except Exception as e:
                    traceback.print_exc()
                    raise HTTPException(status_code=500, detail=str(e))

            super().add_api_route(
                put_url,
                put_rest_template,
                response_model=model,
                methods=['PUT'],
                summary=summary)

        if 'del_summary' in kwargs:
            summary = kwargs['del_summary']
        else:
            summary = 'Deletar '+field_name
        if 'del_url' in kwargs:
            del_url = kwargs['del_url']
        else:
            del_url = url_path+'/{slug_smid:str}'
        if 'del_method' in kwargs and callable(kwargs['del_method']):
            super().add_api_route(
                del_url,
                kwargs['del_method'],
                methods['DELETE'],
                summary=summary)
        elif 'skip_del_method' not in kwargs:
            def del_rest_template(*,
                                  balaio_slug_smid: str,
                                  mucua_slug_smid: str,
                                  slug_smid: str,
                                  token: str = Header(...)):
                try:
                    balaio_smid = self.extract_smid(balaio_slug_smid)
                    mucua_smid = self.extract_smid(mucua_slug_smid)
                    smid = self.extract_smid(slug_smid)
                    getattr(self.baobaxia, 'del_'+field_name)(
                        balaio_smid, mucua_smid, smid, token)
                    return {'detail': 'success'}
                except (SessionNotFound, SessionExpired):
                    traceback.print_exc()
                    raise HTTPException(status_code=401, detail="Token inválido")
                except Exception as e:
                    traceback.print_exc()
                    raise HTTPException(status_code=500, detail=str(e))

            super().add_api_route(
                del_url,
                del_rest_template,
                methods=['DELETE'],
                summary=summary)

    async def authenticate(self, *,
                           username: str = Form(...),
                           password: str = Form(...)):
        try:
            result = self.baobaxia.authenticate(
                username, password)
            return result
        except BaobaxiaError:
            traceback.print_exc()
            raise HTTPException(status_code=400, detail="Erro de autenticação.")

    async def keep_alive(self, *,
                         token: str = Header(...)):
        self.baobaxia.get_session_mocambola(token)
        return {'detail': 'success'}

    async def recover(self, *,
                      username: str = Form(...),
                      recovery_answer: str = Form(...)):
        return self.baobaxia.authenticate(
            username, recovery_answer = recovery_answer)

    async def list_balaios(self, token: Optional[str] = Header(None)):
        try:
            return self.baobaxia.list_balaios(token=token)
        except (SessionNotFound, SessionExpired):
            traceback.print_exc()
            raise HTTPException(status_code=401, detail="Token inválido")
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))

    async def post_balaio(self,
                          name: str = Form(...),
                          default_mucua: str = Form(...),
                          token: str = Header(...)):
        try:
            return self.baobaxia.put_balaio(name=name,
                                            default_mucua=default_mucua,
                                            token=token)
        except (SessionNotFound, SessionExpired):
            traceback.print_exc()
            raise HTTPException(status_code=401, detail="Token inválido")
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))

    async def get_balaio(self, balaio_slug_smid: str,
                         token: Optional[str] = Header(None)):
        try:
            balaio_smid = self.extract_smid(balaio_slug_smid)
            return self.baobaxia.get_balaio(balaio_smid, token=token)
        except (SessionNotFound, SessionExpired):
            traceback.print_exc()
            raise HTTPException(status_code=401, detail="Token inválido")
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))

    async def put_balaio(self, balaio_slug_smid: str,
                         name: str = Form(...), 
                         default_mucua: str = Form(...),
                         token: str = Header(...)):
        try:
            balaio_smid = self.extract_smid(balaio_slug_smid)
            return self.baobaxia.put_balaio(
                smid=balaio_smid,
                name=name,
                default_mucua=default_mucua,
                token=token)
        except (SessionNotFound, SessionExpired):
            traceback.print_exc()
            raise HTTPException(status_code=401, detail="Token inválido")
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))

    async def del_balaio(self, balaio_slug_smid: str, token: str = Header(...)):
        try:
            balaio_smid = self.extract_smid(balaio_slug_smid)
            self.baobaxia.del_balaio(balaio_smid, token=token)
            return {'detail': 'success'}
        except (SessionNotFound, SessionExpired):
            traceback.print_exc()
            raise HTTPException(status_code=401, detail="Token inválido")
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))

    async def list_mucuas(self,
                          balaio_slug_smid: str,
                          token: Optional[str] = Header(None)):
        try:
            balaio_smid = self.extract_smid(balaio_slug_smid)
            return self.baobaxia.list_mucuas(balaio_smid, token=token)
        except (SessionNotFound, SessionExpired):
            traceback.print_exc()
            raise HTTPException(status_code=401, detail="Token inválido")
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))

    async def post_mucua(self,
                         balaio_slug_smid: str,
                         name: str = Form(...),
                         token: str = Header(...)):
        try:
            balaio_smid = self.extract_smid(balaio_slug_smid)
            return self.baobaxia.put_mucua(balaio_smid=balaio_smid,
                                           name=name, token=token)
        except (SessionNotFound, SessionExpired):
            traceback.print_exc()
            raise HTTPException(status_code=401, detail="Token inválido")
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))

    async def get_mucua(self,
                        balaio_slug_smid: str,
                        mucua_slug_smid: str,
                        token: Optional[str] = Header(None)):
        try:
            balaio_smid = self.extract_smid(balaio_slug_smid)
            mucua_smid = self.extract_smid(mucua_slug_smid)
            return self.baobaxia.get_mucua(balaio_smid, mucua_smid,
                                           token=token)
        except (SessionNotFound, SessionExpired):
            traceback.print_exc()
            raise HTTPException(status_code=401, detail="Token inválido")
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))

    async def put_mucua(self,
                        balaio_slug_smid: str,
                        mucua_slug_smid: str,
                        name: str = Form(...),
                        token: str = Header(...)):
        try:
            balaio_smid = self.extract_smid(balaio_slug_smid)
            mucua_smid = self.extract_smid(mucua_slug_smid)
            return self.baobaxia.put_mucua(
                balaio_smid=balaio_smid,
                mucua_smid=mucua_smid,
                name=name, token=token)
        except (SessionNotFound, SessionExpired):
            traceback.print_exc()
            raise HTTPException(status_code=401, detail="Token inválido")
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))

    async def del_mucua(self,
                        balaio_slug_smid: str,
                        mucua_slug_smid: str,
                        token: str = Header(...)):
        try:
            balaio_smid = self.extract_smid(balaio_slug_smid)
            mucua_smid = self.extract_smid(mucua_slug_smid)
            self.baobaxia.del_mucua(balaio_smid, mucua_smid, token=token)
            return {'detail': 'success'}
        except (SessionNotFound, SessionExpired):
            traceback.print_exc()
            raise HTTPException(status_code=401, detail="Token inválido")
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))

    async def set_password(
            self, *,
            balaio_slug_smid: str,
            mucua_slug_smid: str,
            new_password: str = Form(...),
            password: Optional[str] = Form(None),
            recovery_answer: Optional[str] = Form(None),
            token: str = Header(...)):
        try:
            balaio_smid = self.extract_smid(balaio_slug_smid)
            mucua_smid = self.extract_smid(mucua_slug_smid)
            return self.baobaxia.set_password(
                balaio_smid = balaio_smid,
                mucua_smid = mucua_smid,
                new_password = new_password,
                password = password,
                recovery_answer = recovery_answer,
                token = token
            )
        except (SessionNotFound, SessionExpired):
            traceback.print_exc()
            raise HTTPException(status_code=401, detail="Token inválido")
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))

    async def list_mocambolas(self, *,
                        balaio_slug_smid: str,
                        mucua_slug_smid: str,
                        token: Optional[str] = Header(None)):
        try:
            balaio_smid = self.extract_smid(balaio_slug_smid)
            mucua_smid = self.extract_smid(mucua_slug_smid)
            return self.baobaxia.list_mocambolas(
                balaio_smid, mucua_smid, token)
        except (SessionNotFound, SessionExpired):
            traceback.print_exc()
            raise HTTPException(status_code=401, detail="Token inválido")
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))

    async def get_mocambola(self, *,
                      balaio_slug_smid: str,
                      mucua_slug_smid: str,
                      username: str,
                      token: Optional[str] = Header(None)):
        try:
            balaio_smid = self.extract_smid(balaio_slug_smid)
            mucua_smid = self.extract_smid(mucua_slug_smid)
            return self.baobaxia.get_mocambola(
                balaio_smid, mucua_smid, username, token)
        except (SessionNotFound, SessionExpired):
            traceback.print_exc()
            raise HTTPException(status_code=401, detail="Token inválido")
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))

    async def post_mocambola(self, *,
                      balaio_slug_smid: str,
                      mucua_slug_smid: str,
                      mocambola: Mocambola,
                      token: str = Header(...)):
        try:
            balaio_smid = self.extract_smid(balaio_slug_smid)
            mucua_smid = self.extract_smid(mucua_slug_smid)
            return self.baobaxia.put_mocambola(
                balaio_smid, mucua_smid,
                mocambola.username,
                mocambola,
                None,
                token = token
            )
        except (SessionNotFound, SessionExpired):
            traceback.print_exc()
            raise HTTPException(status_code=401, detail="Token inválido")
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))

    async def put_mocambola(self, *,
                      balaio_slug_smid: str,
                      mucua_slug_smid: str,
                      username: str,
                      mocambola: Mocambola,
                      token: str = Header(...)):
        try:
            balaio_smid = self.extract_smid(balaio_slug_smid)
            mucua_smid = self.extract_smid(mucua_slug_smid)
            return self.baobaxia.put_mocambola(
                balaio_smid, mucua_smid,
                username,
                mocambola,
                None,
                token = token
            )
        except (SessionNotFound, SessionExpired):
            traceback.print_exc()
            raise HTTPException(status_code=401, detail="Token inválido")
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))

    async def del_mocambola(self, *,
                      balaio_slug_smid: str,
                      mucua_slug_smid: str,
                      username: str,
                      token: str = Header(...)):
        try:
            balaio_smid = self.extract_smid(balaio_slug_smid)
            mucua_smid = self.extract_smid(mucua_slug_smid)
            self.baobaxia.del_mocambola(
                balaio_smid, mucua_smid, username, token)
            return {'detail': 'success'}
        except (SessionNotFound, SessionExpired):
            traceback.print_exc()
            raise HTTPException(status_code=401, detail="Token inválido")
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))

    async def add_mocambola_balaio(self, *,
                                    balaio_slug_smid: str,
                                    mucua_slug_smid: str,
                                    novo_balaio_slug_smid: str,
                                    username: str,
                                    token: str = Header(...)):
        try:
            mocambola = self.baobaxia.get_session_mocambola(token)
            balaio_smid = self.extract_smid(balaio_slug_smid)
            mucua_smid = self.extract_smid(mucua_slug_smid)
            novo_balaio_smid = self.extract_smid(novo_balaio_slug_smid)
            if not ROLE_MUCUA_PAJE in mocambola.live_roles[balaio_smid]:
                raise HTTPException(status_code=401,
                                    detail='Mocambola não tem permissão')
            return self.baobaxia.add_mocambola_balaio(
                balaio_smid, mucua_smid, novo_balaio_smid, username, token)
        except (SessionNotFound, SessionExpired):
            traceback.print_exc()
            raise HTTPException(status_code=401, detail="Token inválido")
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))


#path = config.data_path / config.balaio_local / config.mucua_local
api = BaobaxiaAPI()

