from pathlib import Path
from datetime import date, datetime
import os
from collections.abc import MutableMapping

from typing import Optional, List, Any
from pydantic import BaseModel
from configparser import ConfigParser 

from .sankofa import Sankofa
from .util import str_to_hash
from .saberes import (
    Saber,
    Balaio,
    Mucua,
    Mocambola,
    SaberesConfig,
    SaberesDataStore
)

class BaobaxiaError(RuntimeError):
    pass

class SessionNotFound(BaobaxiaError):
    pass

class SessionExpired(BaobaxiaError):
    pass

# TODO: Necessário aprimorar a geração do token, para evitar
# que difenrentes instâncias com mesmo mocambola compartilhem
# a sessão.
class Session():

    timeout = 900 # 15 minutos

    def __init__(self, mocambola: Mocambola):
        super().__init__()
        self.mocambola = mocambola
        self.started = datetime.now()
        self.alive_at = datetime.now()
        self.token = str_to_hash(
            mocambola.username +
            str(round(self.started.microsecond * 1000)))

    def is_alive(self, safe = True):
        result = True
        if self.alive_at is None:
            result = False
        else:
            delta = datetime.now() - self.alive_at
            result = self.__class__.timeout > delta.seconds
        if not result and not safe:
            raise SessionExpired('Sessão expirou')
        return result

    def keep_alive(self):
        self.is_alive(False)
        self.alive_at = datetime.now()
        return self

    def close(self):
        self.alive_at = None

class SessionDict(MutableMapping):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._by_token = {}
        self._by_mocambola = {}
        self.update(dict(*args, **kwargs))

    def __contains__(self, key):
        if isinstance(key, Mocambola):
            return key.username in self._by_mocambola
        return key in self._by_token

    def __getitem__(self, key):
        if isinstance(key, Mocambola):
            if key.username in self._by_mocambola and \
                    self._by_mocambola[key.username].is_alive():
                return self._by_mocambola[key.username].keep_alive()
            session = Session(key.copy(exclude={'password_hash',
                                                'recovery_answer_hash'}))
            self[key] = session
            return session
        else:
            if key not in self._by_token:
                raise SessionNotFound("Sessão inválida")
            return self._by_token[key].keep_alive()

    def __setitem__(self, key, value):
        if not isinstance(value, Session):
            raise BaobaxiaError("Sessão inválida")
        value.is_alive(False)
        if isinstance(key, Mocambola) and \
           value.mocambola.username != key.username:
            raise BaobaxiaError("Mocambola inválido")
        if isinstance(key, str) and value.token != key:
            raise BaobaxiaError("Token inválido")
        self._by_mocambola[value.mocambola.username] = value
        self._by_token[value.token] = value

    def __delitem__(self, key):
        session = self[key]
        session.close()
        del self._by_mocambola[session.mocambola.username]
        del self._by_token[session.token]

    def __iter__(self):
        return iter(self._by_token)

    def __len__(self):
        return len(self._by_token)


class Baobaxia():

    def __init__(self, config: Optional[SaberesConfig] = None):
        if config == None:
            config_file = ConfigParser()
            config_file.read(os.path.join(os.path.expanduser("~"),
                                          '.baobaxia.conf'))
            config = SaberesConfig.parse_obj(config_file['default'])
        self.config = config
        self.datastore = SaberesDataStore(self.config)
        self.reload_balaios()
        self._sessions = SessionDict()

    def reload_balaios(self):
        balaios_list = self.datastore.create_balaio_dataset(
            ).find_and_collect('*/')
        self._balaios = {}
        self._mucuas_por_balaio = {}
        self._mocambolas_por_mucua = {}
        self._roles_por_mocambolas = {}
        for balaio in balaios_list:
            self._balaios[balaio.smid] = balaio
            self._mucuas_por_balaio[balaio.smid] = {}
            self._mocambolas_por_mucua[balaio.smid] = {}
            self._roles_por_mocambolas[balaio.smid] = {}
            mucuas = self.datastore.create_mucua_dataset(
                balaio.smid).find_and_collect('*/')
            for mucua in mucuas:
                self._mucuas_por_balaio[balaio.smid][mucua.smid] = mucua
                self._mocambolas_por_mucua[balaio.smid][mucua.smid] = {}
                mocambolas = self.datastore.create_dataset(
                    model=Mocambola, balaio_smid=balaio.smid,
                    mucua_smid=mucua.smid).find_and_collect('mocambolas/*/')
                for mocambola in mocambolas:
                    self._mocambolas_por_mucua[balaio.smid][mucua.smid][
                        mocambola.username] = mocambola
                    self._roles_por_mocambolas[balaio.smid][
                        mocambola.username] = {}
                    self._roles_por_mocambolas[balaio.smid][
                        mocambola.username]["roles"] = mocambola.roles
        
        self.default_balaio = self._balaios[
            self.config.default_balaio]

        self.default_mucua = self._mucuas_por_balaio[
            self.config.default_balaio][
                self.config.default_mucua]


    def list_balaios(self, token: Optional[str] = None):
        session = self._sessions[token] if token else None
        result = []
        for key, value in self._balaios.items():
            if session is not None or value.is_public:
                result.append(value.copy())
        return result

    def get_balaio(self, smid: str, token: Optional[str] = None):
        session = self._sessions[token] if token else None
        if session is not None or self._balaios[smid].is_public:
            return self._balaios[smid].copy()
        return None

    def get_default_balaio(self, token: Optional[str] = None):
        return self.default_balaio

    def put_balaio(self, *,
                   smid: Optional[str] = None,
                   name: str,
                   default_mucua: Optional[str] = None,
                   token: str):
        session = self._sessions[token]
        dataset = self.datastore.create_balaio_dataset(
            mocambola=session.mocambola.username)
        if smid is None:
            balaio = dataset.settle(
                Balaio(
                    name = name,
                    default_mucua = default_mucua)
            )
            self._balaios[balaio.smid] = balaio
            self._mucuas_por_balaio[balaio.smid] = {}
            self._mocambolas_por_mucua[balaio.smid] = {}
            Sankofa.create_balaio(
                balaio = balaio.slug,
                description = balaio.name,
                config=self.config)
            if default_mucua is not None:
                mucua_existe = self.get_mucua_by_smid(
                    mucua_smid=default_mucua)
                if mucua_existe:
                    mucua_name = mucua_existe.name
                else:
                    mucua_name = default_mucua
                mucua = self.put_mucua(
                    balaio_smid = balaio.smid,
                    name = mucua_name,
                    mucua_smid = default_mucua,
                    token = token)
                balaio.default_mucua = mucua.smid
                dataset.settle(balaio)
        else:
            balaio = self._balaios[smid]
            balaio.name = name
            if not default_mucua:
                balaio.default_mucua = self.config.default_mucua
            balaio = dataset.settle(balaio)
            self._balaios[smid] = balaio
        return balaio.copy()

    def del_balaio(self,
                   balaio_smid: str,
                   token: str):
        session = self._sessions[token]
        if balaio_smid == self.default_balaio.smid:
            # Baobaxia não pode deixar para trás o balaio de seus próprios saberes.
            raise RuntimeError('Cannot delete balaio padrão.')
        dataset = self.datastore.create_balaio_dataset(
            mocambola = session.mocambola)
        balaio = self._balaios[balaio_smid]
        Sankofa.destroy_balaio(balaio.slug, config=self.config)
        dataset.drop(balaio.smid)

        del self._balaios[balaio_smid]
        del self._mucuas_por_balaio[balaio_smid]
        del self._mocambolas_por_mucua[balaio_smid]

    def list_mucuas(self,
                    balaio_smid: str,
                    token: Optional[str] = None):
        session = self._sessions[token] if token else None
        result = []
        for key, value in self._mucuas_por_balaio[balaio_smid].items():
            if session is not None or value.is_public:
                result.append(value.copy())
        return result

    def get_mucua(self,
                  balaio_smid: str,
                  mucua_smid: str,
                  token: Optional[str] = None):
        session = self._sessions[token] if token else None
        if session is not None or self._mucuas_por_balaio[
                balaio_smid][mucua_smid].is_public:
            return self._mucuas_por_balaio[balaio_smid][mucua_smid].copy()
        return None

    def get_mucua_by_smid(self, mucua_smid):
        for balaio_smid in self._mucuas_por_balaio:
            if self._mucuas_por_balaio[balaio_smid].get(mucua_smid):
                return self._mucuas_por_balaio[balaio_smid][mucua_smid]
            else:
                return None
    
    def get_default_mucua(self, token: Optional[str] = None):
        return self.default_mucua

    def put_mucua(self, *,
                  balaio_smid: str,
                  name: str,
                  mucua_smid: Optional[str] = None,
                  token: str):
        session = self._sessions[token]
        dataset = self.datastore.create_mucua_dataset(
            balaio_smid=balaio_smid,
            mocambola=session.mocambola.username)
        if mucua_smid is None:
            mucua = dataset.settle(Mucua(name=name))
            self._mucuas_por_balaio[balaio_smid][mucua.smid] = mucua
            self._mocambolas_por_mucua[balaio_smid][mucua.smid] = {}
            mucua.path = self._balaios[balaio_smid].path / mucua.path
            Sankofa.add(saberes=[mucua], mocambola=session.mocambola,
                config=self.config)
        elif mucua_smid is not None and not\
            self._mucuas_por_balaio[balaio_smid].get(mucua_smid):
            mucua = dataset.settle(Mucua(name=name, smid=mucua_smid,
                                         is_public=True))
            self._mucuas_por_balaio[balaio_smid][mucua.smid] = mucua
            self._mocambolas_por_mucua[balaio_smid][mucua.smid] = {}
            mucua.path = self._balaios[balaio_smid].path / mucua.path
            Sankofa.add(saberes=[mucua], mocambola=session.mocambola,
                config=self.config)
        else:
            mucua = self._mucuas_por_balaio[balaio_smid][mucua_smid]
            if name:
                mucua.name = name
            mucua = dataset.settle(mucua)
            mucuapath = Path(mucua.path)
            self._mucuas_por_balaio[balaio_smid][mucua.smid] = mucua
            mucua.path = self._balaios[balaio_smid].path / mucuapath
            Sankofa.add(saberes=[mucua], mocambola=session.mocambola,
                        config=self.config)
        return mucua.copy()

    def del_mucua(self,
                  balaio_smid: str,
                  mucua_smid: str,
                  token: str):
        session = self._sessions[token]
        if balaio_smid == self.default_balaio.smid and \
           mucua_smid == self.default_balaio.mucua_smid:
            # Baobaxia não pode deixar para trás a mucua de seus próprios saberes.
            raise RuntimeError('Cannot delete mucua padrão.')
        
        mucua = self._mucuas_por_balaio[balaio_smid][mucua_smid]

        dataset = self.datastore.create_mucua_dataset(
            balaio_smid=balaio_smid,
            mocambola=session.mocambola.username)

        mucua.path = self._balaios[balaio_smid].path / mucua.path
        Sankofa.remove(saberes=[mucua,],
                       mocambola=session.mocambola,
                       config=self.config)

        dataset.drop(mucua)

        del self._mucuas_por_balaio[balaio_smid][mucua_smid]
        del self._mocambolas_por_mucua[balaio_smid][mucua_smid]

    def list_mocambolas(self,
                        balaio_smid: str,
                        mucua_smid: str,
                        token: str):
        session = self._sessions[token] if token else None
        result = []
        for mocambola in self._mocambolas_por_mucua[
                balaio_smid][mucua_smid].values():
            if session is not None or mocambola.is_public:
                result.append(mocambola.copy(exclude={
                    'password_hash', 'recovery_answer_hash'}))
        return result

    def get_mocambola(self,
                      balaio_smid: str,
                      mucua_smid: str,
                      username: str,
                      token: str):
        session = self._sessions[token] if token else None
        if session is not None or self._mocambolas_por_mucua[
                balaio_smid][mucua_smid][username].is_public:
            return self._mocambolas_por_mucua[balaio_smid][mucua_smid][
                username].copy(exclude={'password_hash', 'recovery_answer_hash'})
        return None

    def put_mocambola(self,
                      balaio_smid: str,
                      mucua_smid: str,
                      username: str,
                      mocambola: Mocambola,
                      recovery_answer: Optional[str] = None, *,
                      token: str):
        session = self._sessions[token]
        dataset = self.datastore.create_dataset(
            model=Mocambola,
            balaio_smid=balaio_smid,
            mucua_smid=mucua_smid,
            mocambola=mocambola)
        if recovery_answer is not None:
            mocambola.recovery_answer_hash = str_to_hash(recovery_answer)
        if username in self._mocambolas_por_mucua[balaio_smid][mucua_smid]:
            mocambola_old = self._mocambolas_por_mucua[balaio_smid][
                mucua_smid][username]
            mocambola.password_hash = mocambola_old.password_hash
            mocambola.recovery_answer_hash = mocambola_old.recovery_answer_hash
            mocambola.smid = mocambola_old.smid
            if mocambola.name != mocambola_old.name:
                mocambola.slug = dataset.create_slug(mocambola.smid, mocambola.name)
                mocambola.path = Path('mocambolas')
            mocambola.live_roles = {}
            mocambola = dataset.settle(mocambola)
            self._mocambolas_por_mucua[balaio_smid][
                mucua_smid][username] = mocambola
            if mocambola in self._sessions:
                a_session = self._sessions[mocambola]
                a_session.mocambola = mocambola
        else:
            mocambola.path = Path('mocambolas')
            mocambola.password_hash = None
            mocambola.recovery_answer_hash = None
            mocambola.live_roles = {}
            mocambola = dataset.settle(mocambola)
            self._mocambolas_por_mucua[balaio_smid][
                mucua_smid][username] = mocambola        
            mocambola.path = self._balaios[
                balaio_smid].path / self._mucuas_por_balaio[
                    balaio_smid][mucua_smid].path / mocambola.path
            Sankofa.add(saberes=[mocambola], mocambola=session.mocambola,
                config=self.config)
        return mocambola.copy(exclude={'password_hash', 'recovery_answer_hash'})

    def del_mocambola(self,
                      balaio_smid: str,
                      mucua_smid: str,
                      username: str,
                      token: str):
        session = self._sessions[token]
        mocambola = self._mocambolas_por_mucua[
            balaio_smid][mucua_smid][username]
        dataset = self.datastore.create_dataset(
            model=Mocambola,
            balaio_smid=balaio_smid,
            mucua_smid=mucua_smid,
            mocambola=session.mocambola).drop(mocambola.path)
        del self._mocambolas_por_mucua[balaio_smid][mucua_smid][username]
        
        mocambola.path = self._balaios[
            balaio_smid].path / self._mucuas_por_balaio[
                balaio_smid][mucua_smid].path / mocambola.path
        Sankofa.remove(saberes=[mocambola,], mocambola=session.mocambola,
                       config=self.config)

    def add_mocambola_balaio(self,
                             balaio_smid: str,
                             mucua_smid: str,
                             novo_balaio_smid: str,
                             username: str,
                             token: str):
        session = self._sessions[token]
        mocambola = self._mocambolas_por_mucua[
            balaio_smid][mucua_smid][username]
        mocambola.balaio_smid = novo_balaio_smid
        dataset = self.datastore.create_dataset(
            model=Mocambola,
            balaio_smid=novo_balaio_smid,
            mucua_smid=mucua_smid,
            mocambola=mocambola)
        mocambola = dataset.settle(mocambola)
        mocambola.path = self._balaios[
            novo_balaio_smid].path / self._mucuas_por_balaio[
                novo_balaio_smid][mucua_smid].path / mocambola.path
        Sankofa.add(saberes=[mocambola], mocambola=mocambola,
                config=self.config)
        self._mocambolas_por_mucua[novo_balaio_smid][
            mucua_smid][username] = mocambola 
        return True

    def get_session_mocambola(self, token: str):
        return self._sessions[token].mocambola

    def _add_to_index(self,
                      balaio: str,
                      mucua: str,
                      field: str,
                      saber: Saber):
        if field not in self.indexes_names:
            return
        if balaio not in self.indexes:
            self.indexes[balaio] = {}
        if mucua not in self.indexes[balaio]:
            self.indexes[balaio][mucua] = {}
        if field not in self.indexes[balaio][mucua]:
            self.indexes[balaio][mucua][field] = {}
        for idx in self.indexes_names[field]:
            if idx not in self.indexes[balaio][mucua][field]:
                self.indexes[balaio][mucua][field][idx] = {}
            val = getattr(saber, idx)
            if isinstance(val, list):
                for val_item in val:
                    if val_item not in self.indexes[balaio][mucua][field][idx]:
                        self.indexes[balaio][mucua][field][idx][
                            val_item] = set()
                    self.indexes[balaio][mucua][field][idx][
                        val_item].add(saber.smid)
            else:
                if val not in self.indexes[balaio][mucua][field][idx]:
                    self.indexes[balaio][mucua][field][idx][val] = set()
                self.indexes[balaio][mucua][field][idx][val].add(saber.smid)
    
    def _remove_from_index(self,
                           balaio: str,
                           mucua: str,
                           field: str,
                           saber: Saber):
        if field not in self.indexes_names:
            return
        if balaio not in self.indexes:
            return
        if mucua not in self.indexes[balaio]:
            return
        if field not in self.indexes[balaio][mucua]:
            return
        for idx in self.indexes_names[field]:
            if idx not in self.indexes[balaio][mucua][field]:
                continue
            val = getattr(saber, idx)
            if isinstance(val, list):
                for val_item in val:
                    if val_item not in self.indexes[balaio][mucua][field][idx]:
                        continue
                    self.indexes[balaio][mucua][field][idx][
                        val_item].discard(saber.smid)
            else:
                if val not in self.indexes[balaio][mucua][field][idx]:
                    continue
                self.indexes[balaio][mucua][field][idx][
                    val].discard(saber.smid)

    def get_path_by_index(self,
                           balaio_smid: str,
                           mucua_smid: str,
                           field: str,
                           index: str,
                           value: Any):
            result = []
            if balaio_smid not in self.indexes and \
               mucua_smid in self.indexes[balaio_smid] and \
               field in self.indexes[balaio_smid][mucua_smid] and \
               index in self.indexes[balaio_smid][mucua_smid][field] and \
               value in self.indexes[balaio_smid][mucua_smid][field][index]:
                    # FIX o que seria expand?
                result.expand(self.indexes[
                    balaio_smid][mucua_smid][field][index][value])
            return result

    def _check_cache(self, 
                        model: type, 
                        field: str,
                        patterns: List[str],
                        balaio_smid: str,
                        mucua_smid: str,
                        update: bool = False):
        if not update and \
                balaio_smid in self.saberes and \
                mucua_smid in self.saberes[balaio_smid] and \
                field in self.saberes[balaio_smid][mucua_smid]:
            return
        if balaio_smid not in self.saberes:
            self.saberes[balaio_smid] = {}
        if mucua_smid not in self.saberes[balaio_smid]:
            self.saberes[balaio_smid][mucua_smid] = {}
        self.saberes[balaio_smid][mucua_smid][field] = {}

        if balaio_smid not in self.indexes:
            self.indexes[balaio_smid] = {}
        if mucua_smid not in self.indexes[balaio_smid]:
            self.indexes[balaio_smid][mucua_smid] = {}
        self.indexes[balaio_smid][mucua_smid][field] = {}
        for idx_name in self.indexes_names:
            self.indexes[balaio_smid][mucua_smid][field][idx_name] = {}

        dataset = self.datastore.create_dataset(
            model = model,
            balaio_smid = balaio_smid,
            mucua_smid = mucua_smid)

        for pattern in patterns:
            saberes = dataset.find_and_collect(pattern)
            for saber in saberes:
                self.saberes[balaio_smid][mucua_smid][
                    field][saber.smid] = saber
                self._add_to_index(balaio_smid, mucua_smid, field, saber)

    def discover_saberes(self, *,
                         model: type,
                         patterns: List[str],
                         field_name: Optional[str] = None,
                         list_field_name: Optional[str] = None,
                         indexes_names: List[str] = []
    ):
        if field_name is None:
            field_name = model.__name__.lower()
        if list_field_name is None:
            list_field_name = field_name + 's'

        if not hasattr(self, 'saberes'):
            self.saberes = {}
        if not hasattr(self, 'indexes'):
            self.indexes = {}
        if not hasattr(self, 'indexes_names'):
            self.indexes_names = {}
        self.indexes_names[field_name] = indexes_names

        def list_method_template(balaio_smid: str, mucua_smid: str, token: str):
            session = self._sessions[token] if token else None
            self._check_cache(model, field_name, patterns,
                              balaio_smid, mucua_smid)
            result = []
            for key, saber in self.saberes[balaio_smid][mucua_smid][
                    field_name].items():
                if session is not None or saber.is_public:
                    result.append(saber.copy())
            return result
        setattr(self, 'list_'+list_field_name, list_method_template)
        
        def find_method_template(
                balaio_smid: str, mucua_smid: str, token: str,
                filter_function: Optional[callable] = None,
                sorted_function: Optional[callable] = None,
                sorted_reverse: bool = False,
                page_size: int = 0,
                page_index: int = 0):
            session = self._sessions[token] if token else None
            self._check_cache(model, field_name, patterns,
                              balaio_smid, mucua_smid)
            result = []
            page_count = 0
            page_item_count = 0
            for key, saber in self.saberes[balaio_smid][mucua_smid][
                    field_name].items():
                if session is not None and saber.is_public:
                    if filter_function is None or filter_function(saber):
                        page_item_count += 1
                        if page_count == 0:
                            page_count = 1
                        elif page_item_count > page_size:
                            page_count += 1
                            page_item_count = 0
                        if page_count < page_index:
                            continue
                        elif page_count > page_index:
                            break
                    result.append(saber.copy())
            if sorted_function is not None:
                result = sorted(result, key = sorted_function,
                                reverse = sorted_reverse)
            return result
        setattr(self, 'find_'+list_field_name, find_method_template)

        def get_method_template(balaio_smid: str, mucua_smid: str,
                                smid: str, token: str):
            session = self._sessions[token] if token else None
            self._check_cache(model, field_name, patterns,
                              balaio_smid, mucua_smid)
            if smid in self.saberes[balaio_smid][mucua_smid][field_name]:
                if session is not None or self.saberes[
                        balaio_smid][mucua_smid][field_name][smid].is_public:
                    return self.saberes[
                        balaio_smid][mucua_smid][field_name][smid].copy()
            return None
        setattr(self, 'get_'+field_name, get_method_template)

        def put_method_template(balaio_smid: str,
                                mucua_smid: str,
                                saber: model,
                                token: str):
            session = self._sessions[token]
            self._check_cache(model, field_name, patterns,
                              balaio_smid, mucua_smid)
            saber = self.datastore.create_dataset(
                    model = model,
                    balaio_smid = balaio_smid,
                    mucua_smid = mucua_smid,
                    mocambola = session.mocambola).settle(saber)
            if saber.smid in self.saberes[balaio_smid][mucua_smid][field_name]:
                self._remove_from_index(balaio_smid, mucua_smid, field_name,
                    self.saberes[
                        balaio_smid][mucua_smid][field_name][saber.smid])
            self.saberes[balaio_smid][mucua_smid][
                field_name][saber.smid] = saber
            self._add_to_index(balaio_smid, mucua_smid, field_name, saber)

            saber_sankofa = saber.copy()

            saber_sankofa.path = self._balaios[
                balaio_smid].path / self._mucuas_por_balaio[
                    balaio_smid][mucua_smid].path / saber.path
            #saber_sankofa.path = self._mucuas_por_balaio[balaio_smid][
            #    mucua_smid].path / saber.path
            Sankofa.add(saberes=[saber_sankofa], mocambola=session.mocambola,
                        config=self.config)
            
            return saber.copy()
        setattr(self, 'put_'+field_name, put_method_template)

        def del_method_template(balaio_smid: str, mucua_smid: str,
                                smid: str, token: str):
            session = self._sessions[token]
            self._check_cache(model, field_name, patterns,
                              balaio_smid, mucua_smid)
            dataset = self.datastore.create_dataset(
                model = model,
                balaio_smid = balaio_smid,
                mucua_smid = mucua_smid,
                mocambola = session.mocambola)
            saber = self.saberes[balaio_smid][mucua_smid][
                 field_name][smid]
            saber.path = self._balaios[balaio_smid].path / self._balaio.path
            Sankofa.remove(saberes=[saber], mocambola=session.mocambola,
                           config=self.config)
            del self.saberes[balaio_smid][mucua_smid][
                 field_name][smid]
            self._remove_from_index(balaio_smid, mucua_smid, field_name, saber)
            dataset.drop(saber.path)
        setattr(self, 'del_'+field_name, del_method_template)

    def _check_hash(self, *,
                    balaio_smid: str,
                    mucua_smid: str,
                    username: str,
                    password: Optional[str] = None,
                    recovery_answer: Optional[str] = None):
        mocambola = self._mocambolas_por_mucua[
            balaio_smid][mucua_smid][username]
        str_to_check = None
        hash_to_check = None
        if password is not None:
            str_to_check = password
            hash_to_check = mocambola.password_hash
        elif recovery_answer is not None:
            str_to_check = recovery_answer
            hash_to_check = mocambola.recovery_answer_hash
        else:
            raise BaobaxiaError('Erro de autenticação')
        if str_to_hash(str_to_check) != hash_to_check:
#            print([str_to_check, str_to_hash(str_to_check), hash_to_check])
            raise BaobaxiaError('Erro de autenticação')
        return mocambola

    class AuthResponse(BaseModel):
        token: str
        mocambola: Mocambola

    def authenticate(self,
                    username: str,
                    password: Optional[str] = None,
                    recovery_answer: Optional[str] = None):
        mocambola = self._check_hash(
            username = username,
            password = password,
            recovery_answer = recovery_answer,
            balaio_smid = self.default_balaio.smid,
            mucua_smid = self.default_mucua.smid
        )
        mocambola.live_roles = { balaio_smid : self._roles_por_mocambolas[
            balaio_smid][mocambola.username]["roles"] for balaio_smid in \
                                 self._roles_por_mocambolas if \
                                 self._roles_por_mocambolas[
                                     balaio_smid].get(mocambola.username) }
        return self.AuthResponse(
            token=self._sessions[mocambola].token,
            mocambola=mocambola.copy(exclude={
                'password_hash', 'recovery_answer_hash'}))
        
    def set_password(
            self, *,
            balaio_smid: str,
            mucua_smid: str,
            new_password: str,
            password: Optional[str] = None,
            recovery_answer: Optional[str] = None,
            token: str):
        session = self._sessions[token].keep_alive()
        mocambola = session.mocambola
        self._check_hash(
            balaio_smid = balaio_smid,
            mucua_smid = mucua_smid,
            username = mocambola.username,
            password = password,
            recovery_answer = recovery_answer
        )
        mocambola.password_hash = str_to_hash(new_password)
        dataset = self.datastore.create_dataset(
            Mocambola, mocambola.balaio_smid, mocambola.mucua_smid, mocambola)
        mocambola = dataset.settle(mocambola)

    def set_recovery(
            self, *,
            new_recovery_question: str,
            new_recovery_answer: str,
            password: Optional[str] = None,
            recovery_answer: Optional[str] = None,
            token: str):
        session = self._sessions[token].keep_alive()
        mocambola = session.mocambola
        self._check_hash(
            username = mocambola.username,
            password = password,
            recovery_answer = recovery_answer
        )
        mocambola.recovery_question = new_recovery_question
        mocambola.recovery_answer_hash = str_to_hash(new_recovery_answer)
        dataset = self.datastore.create_dataset(
            Mocambola, mocambola.balaio_smid, mocambola.mucua_smid, mocambola)
        mocambola = dataset.settle(mocambola)

