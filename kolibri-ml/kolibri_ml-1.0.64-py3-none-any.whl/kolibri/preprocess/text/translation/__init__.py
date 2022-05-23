from kolibri.preprocess.text.translation.client import Translator as ApiTranslator
from kolibri.preprocess.text.translation.constants import LANGCODES, LANGUAGES  # noqa
from kolibri.preprocess.text.translation.translate import Translator
from kolibri.preprocess.text.translation.utils import validate_text
__api_translator=ApiTranslator()

def translate(text, to_lang=None, from_lang='auto'):

    translated=[]
    texts=validate_text(str(text))
    if not isinstance(texts, list):
        texts=[texts]

    for text in texts:
        try:
            translated.append(__api_translator.translate(text=text, dest=to_lang, src=from_lang))
        except Exception as e:
            print(e)
            print('using standard api')
            translated.append(Translator().translate(text, dest=to_lang, src=from_lang))

    if translated:
        translated_= '\n'.join([t.text for t in translated if t])
        language='unk'
        if translated[0] is not None:
            language=translated[0].src

        return language, translated_
    else:
        return "", ""

