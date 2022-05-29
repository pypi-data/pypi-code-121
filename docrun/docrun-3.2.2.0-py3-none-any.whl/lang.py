from locale import getdefaultlocale

try:
    from zh import langs as lang_zh
    from en import langs as lang_en
except Exception as e:
    try:
        from .zh import langs as lang_zh
        from .en import langs as lang_en
    except Exception as e:
        from docrun.zh import langs as lang_zh
        from docrun.en import langs as lang_en

    pass

class Language:
    lang_config = 'zh' ;
    lang_dict = {
        "zh"  : lang_zh,
        "en"  : lang_en,
    }
    def lang(self,term,*args,**kwargs):
        try:
            text = term
            if term in self.lang_dict[ self.lang_config ]:
                text = self.lang_dict[ self.lang_config ][ term ];
                if not text and term in self.lang_dict['en']:
                    text = self.lang_dict['en'][ term ]
                    pass
            elif term in self.lang_dict['en']:
                text = self.lang_dict['en'][ term ]
            else: text = term
            if not text: text = term
            text = text.format( *args, **kwargs )
        except Exception as e:
            #print('lang error for:',e)
            pass
        return text

    def set_language(self,lan):
        if lan in ('English','en','en_US'):
            self.lang_config = 'en'
        else:
            self.lang_config = 'zh'
        pass

    def add_lang(self,lan,dic):
        if lan in self.lang_dict:
            self.lang_dict[lan].update(dic)
        else:
            self.lang_dict['en'].update(dic)
            pass
        pass
    pass



lang = Language()
lang.set_language( getdefaultlocale()[0] )
set_lang = lang.set_language
is_en = lambda: True if lang.lang_config == 'en' else False
add_lang = lang.add_lang
lt = lang.lang

