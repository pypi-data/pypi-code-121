import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Union, List, Optional, Any

import shortuuid
from slugify import slugify

from pydantic import BaseModel, EmailStr, ValidationError, validator

from .util import GeoLocation

NoneType = type(None)

class SaberesConfig(BaseModel):
    """
    Modelo de configuração do Saber. 
    Essa classe é usada para armazenar algumas configurações de base do Baobáxia.

    Configuração disponível no arquivo: /home/mocambola/.baobaxia.conf
    """

    data_path: Path
    saber_file_ext: str = '.baobaxia'
    
    default_balaio: str
    default_mucua: str

    smid_len: int = 13
    slug_smid_len: int = 7
    slug_name_len: int = 7
    slug_sep: str = '_'

class Saber(BaseModel):
    """Modelo da classe Saber

    Os Saberes são informações memorizadas nas mucuas em formato
    textual e anexo arquivos binarios como imagens, documentos,
    audios, videos.
    
    :param smid: Id do Saber (SmallID)
    :type smid: str
    :param name: Nome do saber
    :type name: str
    :param slug: Identificativo do Saber, gerado pelo nome e id (Name + Smid)
    :type slug: str
    :param path: Caminho do Saber (Path)
    :type path: str
    :param balaio: Balaio de base do Saber (SLUG)
    :type balaio: str, Optional
    :param mucua: Mucua de base do Saber (SLUG)
    :type mucua: str, Optional
    :param application: Aplicação padrão para este tipo de Saber
    :type application: str
    :param created: Data de gravação
    :type created: datetime
    :param creator: Mocambola gravador
    :type creator: str
    :param last_update: Data do ultimo manejo
    :type last_update: datetime
    :param data: Modelo de dados especifico do Saber (BaseModel). 
    :type data: BaseModel, optional

    """
    name: str
    path: Path = Path('.')
    smid: Optional[str] = None
    slug: Optional[str] = None

    balaio_smid: Optional[str] = None
    mucua_smid: Optional[str] = None

    content: List[Path] = []

    application: str = "root"

    created: Optional[datetime] = None
    creator: Optional[str] = None 
    last_update: Optional[datetime] = None

    is_public: bool = False

class Mocambola(Saber):
    """
    Modelo da classe Mocambola.

    Mocambolas somos nois \\o//
    
    :param email: Email do mocambola
    :type email: emailStr, optional
    :param mocambo: Mocambo de base (SMID) 
    :type mocambo: str, optional
    :param username: Username do mocambola
    :type username: str
    :param name: Nome do mocambola
    :type name: str, optional
    :param is_native: Nativo por padrã não (False)
    :type is_native: str, false
    :param family: Familia do mocambola
    :type family: str, optional
    
    :param password_hash: Hash da senha
    :type password_hash: str
    :param validation_code: Codigo de validação
    :type validation_code: str
    
    """
    
    email: Optional[EmailStr] = None
    mocambo: Optional[str] = None
    username: str
    name: Optional[str] = None    

    is_native: bool = False
    roles: List[str] = []
    live_roles: Optional[Dict] = None
    family: Optional[str] = None

    password_hash: Optional[str] = None

    recovery_question: Optional[str] = None
    recovery_answer_hash: Optional[str] = None

class Balaio(Saber):
    """
    Modelo da classe Balaio. 

    Balaio é o lugar onde guarda as coisas, e também uma pasta gerenciada
    com git-annex.
    
    """
    default_mucua: Optional[str] = None

class Mucua(Saber):
    """
    Modelo da classe Mucua. 
    
    Mucua è um nó da rede Baobáxia, e também é o fruto do Baobá.
    """
    pass

class SaberIndexed(BaseModel):
    path: Path
    saber: Saber

class SaberesDataStore():
    """
    Classe para armazenar os Saberes em memória e criar objetos de acesso (SaberesDataset).

    :param config: Objeto de configuração SaberConfig
    :type config: SaberConfig
    
    """

    def __init__(self, config: SaberesConfig):
        """Metodo construtor
        """
        super().__init__()
        self.config = config
        self.clear_cache()

    def clear_cache(self):
        """Limpa a cache
        """
        self._balaios = {}
        self._saberes = {}

    def cache(self, saber: Saber):
        """Coloca o Saber na cache
        
        :param saber: Objeto Saber a ser memorizado na cache
        :type saber: Saber

        """
        path = Path('.')
        if saber.balaio_smid is None:
            path = path / saber.path
            self._balaios[saber.smid] = SaberIndexed(
                path = path, saber = saber
            )
        else:
            if saber.balaio_smid not in self._saberes:
                self._saberes[saber.balaio_smid] = {}
            if saber.mucua_smid is not None:
                path = path / self._saberes[saber.balaio_smid][
                    saber.mucua_smid].path
            path = path / saber.path
            self._saberes[saber.balaio_smid][saber.smid] = SaberIndexed(
                path = path, saber = saber
            )

        
    def uncache(self, smid: str, balaio_smid: Optional[str] = None):
        """Remove o objeto do cache

        :param saber: Objeto Saber a ser removido da cache
        :type saber: Saber

        """
        saber = None
        if balaio_smid is None:
            saber = self._balaios[smid].saber
            del self._balaios[smid]
        else:
            saber = self._saberes[saber.balaio_smid][smid].saber
            del self._saberes[saber.balaio_smid][smid]
        return saber

    def get_cache(self, smid: str, balaio_smid: Optional[str] = None):
        if balaio_smid is None:
            return self._balaios[smid]
        else:
            return self._saberes[balaio_smid][smid]
    
    def get_cached_saber(self, smid: str, balaio_smid: Optional[str] = None):
        return self.get_cache(smid, balaio_smid).saber
    
    def get_cached_path(self, smid: str, balaio_smid: Optional[str] = None):
        path = Path('.')
        if balaio_smid is not None:
            path = path / self.get_cached_path(balaio_smid)
        return path / self.get_cache(smid, balaio_smid).path

    def is_cached(self, smid: str, balaio_smid: Optional[str] = None):
        if balaio_smid is None:
            return smid in self._balaios
        else:
            return balaio_smid in self._saberes and smid in self._saberes[balaio_smid]

    def create_dataset(self, model: type, balaio_smid: str, mucua_smid: str,
                       mocambola: Optional[str] = None):
        return SaberesDataset(self, model, balaio_smid, mucua_smid, mocambola)

    def create_balaio_dataset(self, mocambola: Optional[str] = None):
        return SaberesDataset(self, Balaio, None, None, mocambola)

    def create_mucua_dataset(self, balaio_smid: str,
                             mocambola: Optional[str] = None):
        return SaberesDataset(self, Mucua, balaio_smid, None, mocambola)

class SaberesDataset():
    """Classe usada para criar e manejar os saberes.
    """

    def __init__(self,
                 datastore: SaberesDataStore,
                 model: type,
                 balaio_smid: Optional[str] = None,
                 mucua_smid: Optional[str] = None,
                 mocambola: Optional[str] = None):
        super().__init__()
        self.datastore = datastore
        self.model = model
        self.balaio_smid = balaio_smid
        self.mucua_smid = mucua_smid
        self.mocambola = mocambola
        self.base_path = None
        

    def get_base_path(self):
        """Retorna o caminho básico usado pelo Dataset.
        """
        self.base_path = self.datastore.config.data_path
        if self.balaio_smid is not None:
            if self.mucua_smid is None:
                self.base_path = self.base_path / self.datastore.get_cached_path(
                    smid=self.balaio_smid)
            else:
                self.base_path = self.base_path / self.datastore.get_cached_path(
                    smid=self.mucua_smid, balaio_smid=self.balaio_smid)
        return self.base_path

        
    def get_dir_path(self, smid: str):
        """Retorna o caminho de um saber (existente ou não) 
        dentro do contexto do Dataset.
        """
        return self.datastore.config.data_path / \
                self.datastore.get_cached_path(smid, self.balaio_smid)

    def get_file_path(self, smid: str):
        """Retorna o caminho do arquivo de metadados
        de um saber (existente ou não) 
        dentro do contexto do Dataset.
        """
        return self.get_dir_path(smid) / \
                self.datastore.config.saber_file_ext

    def read_file(self, path: Path):
        """Retorna um saber armazenado em um arquivo.
        """
        return self.model.parse_file(path)

    def create_smid(self):
        """Cria um identificador aleatório pequeno (small id).
        """
        return shortuuid.ShortUUID().random(
            length=self.datastore.config.smid_len)

    def create_slug(self, smid: str, name: str):
        """Cria uma chave para o saber, usando o identificador 
        e o nome atribuído.
        """
        result = slugify(name)
        if len(result) > self.datastore.config.slug_name_len:
            result = result[:self.datastore.config.slug_name_len]
        result += self.datastore.config.slug_sep
        if len(smid) > self.datastore.config.slug_smid_len:
            result += smid[:self.datastore.config.slug_smid_len]
        else:
            result += smid
        return result

    def find_and_collect(self, pattern: str):
        """Busca e coleta saberes a partir de um padrão para 
        caminhos de arquivos.
        """
        result = []
        baobaxia_files = self.get_base_path().glob(
            pattern+self.datastore.config.saber_file_ext)
        for bf in baobaxia_files:
            result_item = self.read_file(path=bf)
            result.append(result_item.copy())
            self.datastore.cache(result_item)
        return result

    def collect(self, path: Path):
        """Coleta um saber.
        """
        result = self.read_file(self.get_file_path(path))
        self.datastore.cache(result)
        return result.copy()

    def get(self, smid: str):
        """Retorna um saber armazenado em cache.
        """
        return self.datastore.get_cached_saber(
                    smid, self.balaio_smid)

    def settle(self, saber: Saber):
        """Assenta um saber em seu arquivo correspondente.
        """
        if self.mocambola is None:
            raise RuntimeError('Dataset is readonly (no mocambola defined)')
        if saber.balaio_smid is None:
            saber.balaio_smid = self.balaio_smid
        if saber.mucua_smid is None:
            saber.mucua_smid = self.mucua_smid
        if saber.smid is not None and self.datastore.is_cached(
                    saber.smid, saber.balaio_smid):
            saber_old = self.datastore.get_cached_saber(
                        saber.smid, saber.balaio_smid)
            saber.created = saber_old.created
            saber.creator = saber_old.creator
            if saber.name != saber_old.name:
                saber.slug = self.create_slug(saber.smid, saber.name)
                saber.path = saber.slug
                p = Path(self.get_file_path(saber.smid)).parent
                saberpath = Path(p)
                saberdirpath = Path(saberpath.parent)
                saberpath.rename(saberdirpath / Path(saber.path))
        else:
            if saber.slug is None:
                if saber.smid is None:
                    saber.smid = self.create_smid()
                saber.slug = self.create_slug(saber.smid, saber.name)
                saber.path = saber.path / saber.slug
            saber.created = datetime.now()
            if isinstance(self.mocambola, Mocambola):
                saber.creator = self.mocambola.username
            else:
                saber.creator = self.mocambola
        saber.last_update = datetime.now()
        self.datastore.cache(saber)
        dirpath = self.get_dir_path(saber.smid)
        if not dirpath.exists():
            dirpath.mkdir(parents=True)
        filepath = self.get_file_path(saber.smid)
        if not filepath.exists():
            filepath.touch()
        filepath.open('w').write(saber.json())

        return saber.copy()

    def drop(self, smid: str):
        """Abandona um saber.
        """
        if self.mocambola is None:
            raise RuntimeError('Dataset is readonly (no mocambola defined)')
        if self.datastore.is_cached(smid, self.balaio_smid):
            saber = self.datastore.get_cached_saber(smid, self.balaio_smid)
            self.datastore.uncache(saber.smid, self.balaio_smid)
