"""
Si vous avez **google cloud translate apikey**, veuillez utiliser :class:`pygtrans.ApiKeyTranslate`

compétences de base:
     #. Détection de la langue, prise en charge de la détection par lots
     #. Traduction de texte, prise en charge par lot, prise en charge de la traduction en mode html
"""
import base64
import random
from typing import List, Union, overload, Dict

import requests


class Translate:
    """
        :Param target: Str: (Kě xuǎn) mùbiāo yǔyán, mòrèn: ``Zh-CN``, :Doc:`Chákàn wánzhěng lièbiǎo <target>` :Param source: Str: (Kě xuǎn) yuán yǔyán, mòrèn: ``Auto`` (zìdòng jiǎncè), :Doc:`Chákàn wánzhěng lièbiǎo <source>` :Param _format: Str: (Kě xuǎn) wénběn géshì, ``text``| ``html``, mòrèn: ``Html`` :Param user_agent: Str: (Kě xuǎn) yònghù dàilǐ, zhège cānshù hěn zhòngyào, bù shèzhì huò cuòwù shèzhì fēicháng róngyì chùfā**429 Too Many Requests** cuòwù, mòrèn: ``GoogleTranslate/6.18.0.06.376053713 (Linux; U; Android 11; GM1900)``, suǒyǐ yònghù kěyǐ bùyòng tígōng. Zhège mòrèn ``User-Agent``hěn wěndìng, zhànshí wèi fāxiàn ``429 cuòwù ``, rúguǒ chūxiàn ``429``, jiànyì**mófǎng mòrèn jìnxíng gòuzào**, huòzhě jìnxíng `fǎnkuì <https://Github.Com/foyoux/pygtrans/issues/new>`_ :Param domain: Str: (Kě xuǎn) yùmíng ``google.Com``jí qí kěyòng píngxíng yùmíng (rú: ``Google.Cn``), mòrèn: ``Google.Cn`` :Param proxies: (Kě xuǎn) eg: Proxies = { 'http': 'Http://Localhost:10809', 'Https': 'Http://Localhost:10809'
        Afficher plus
        786 / 5000
        Résultats de traduction
        :param cible : str : (facultatif) langue cible, par défaut : ``zh-CN``, :doc:`Afficher la liste complète <target>`
            :param source: str: (facultatif) langue source, par défaut : ``auto`` (détection automatique), :doc:`Afficher la liste complète <source>`
            :param _format: str: (facultatif) format de texte, ``text`` | ``html``, par défaut : ``html``
            :param user_agent: str: (facultatif) agent utilisateur, ce paramètre est très important, il est très facile de déclencher l'erreur **429 Too Many Requests** s'il n'est pas défini ou défini de manière incorrecte.
                Par défaut : ``GoogleTranslate/6.18.0.06.376053713 (Linux ; U ; Android 11 ; GM1900)'', les utilisateurs n'ont donc pas besoin de le fournir.
                Le ``User-Agent'' par défaut est très stable, et ``429 error'' n'a pas été trouvé pour le moment. Si ``429'' apparaît, il est recommandé d'**imiter la valeur par défaut pour construire** ,
                Ou donnez votre avis <https://github.com/foyoux/pygtrans/issues/new>`_
            :param domain: str: (facultatif) nom de domaine ``google.com'' et ses noms de domaine parallèles disponibles (par exemple ``google.cn''), par défaut : ``google.cn''
            :param proxys: (facultatif) par exemple : proxys = {
                    'http':'http://localhost:10809',
                    'https':'http://localhost:10809'
        }


    """

    def __init__(
            self,
            target: str = 'zh-CN',
            source: str = 'auto',
            _format='html',
            user_agent: str = None,
            domain: str = 'be',
            proxies: Dict = None
    ):
        self.target = target
        self.source = source
        self.format = _format

        if user_agent is None:
            user_agent = f'GoogleTranslate/6.{random.randint(10, 100)}.0.06.{random.randint(111111111, 999999999)} (Linux; U; Android {random.randint(5, 11)}; {base64.b64encode(str(random.random())[2:].encode()).decode()})'

        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': user_agent
        }
        self.BASE_URL: str = 'https://translate.google.' + domain
        self.LANGUAGE_URL: str = f'{self.BASE_URL}/translate_a/l'
        self.DETECT_URL: str = f'{self.BASE_URL}/translate_a/single'
        self.TRANSLATE_URL: str = f'{self.BASE_URL}/translate_a/t'
        self.TTS_URL: str = f'{self.BASE_URL}/translate_tts'

        if proxies is not None:
            self.session.proxies = proxies

    # @lru_cache
    # def languages(self, target: str = None) -> List[LanguageResponse]:
    #     """获取语言列表
    #
    #     :param target: 列表显示的语言, 默认: ``self.target``
    #     :return: 返回 :func:`pygtrans.LanguageResponse.LanguageResponse` 对象列表
    #
    #     基本用法:
    #         >>> from pygtrans import Translate
    #         >>> client = Translate()
    #         >>> langs = client.languages()
    #         >>> langs[0]
    #         LanguageResponse(language='auto', name='检测语言')
    #     """
    #     if target is None:
    #         target = self.target
    #     response = self.session.get(self.LANGUAGE_URL, params={
    #         'hl': target,
    #         'ie': 'UTF-8',
    #         'oe': 'UTF-8',
    #         'client': 'at'
    #     })
    #     if response.status_code != 200:
    #         return Null(response)
    #     return [LanguageResponse(language=i[0], name=i[1]) for i in response.json()['sl'].items()]
    #     # return [LanguageResponse(language=i[0], name=i[1]) for i in response.json()['tl'].items()]

    def detect(self, q: str):
        """
        """
        response = self.session.post(
            self.DETECT_URL,
            params={'dj': 1, 'sl': 'auto', 'ie': 'UTF-8', 'oe': 'UTF-8', 'client': 'at'},
            data={'q': q}
        )
        if response.status_code != 200:
            return None
        rt = response.json()
        return rt['src'], rt['confidence']

    def translate(self, text, target, source=None, _format=None):
        if not text:
            return {}
        one_item_list = False
        if not isinstance(text, list):
            text=[text, ""]
        elif len(text)==1:
            text.append("")
            one_item_list=True

        response = self._translate(q=text, target=target, source=source, _format=_format)

        if response.status_code == 200:
            rt = response.json()
            if isinstance(text, str):
                rt["results"].pop()
                return rt["results"][0]
            elif one_item_list:
                rt["results"].pop()


        return '\n'.join(s["trans"] for s in rt["results"][0]["sentences"]),  rt["results"][0]["src"]

    def _translate(
            self, q: Union[str, List[str]], target: str = None, source: str = None, _format: str = None, v: str = None
    ):
        if target is None:
            target = self.target
        if source is None:
            source = self.source
        if _format is None:
            _format = self.format
        response = self.session.post(
            self.TRANSLATE_URL,
            params={'tl': target, 'sl': source, 'ie': 'UTF-8', 'oe': 'UTF-8', 'client': 'at', 'dj': '1',
                    'format': _format, 'v': v},
            data={'q': q}
        )
        return response

