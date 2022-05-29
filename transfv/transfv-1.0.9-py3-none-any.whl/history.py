from . import constants
from .obj import debug

class History:

    def __init__( self ):

        self.text = ""
        self.text_trans = ""
        self.first_lang = ""
        self.second_lang = ""
        
        debug("init history")
    

    def set_langs( self ):

        if not self.text:
            self.first_lang = constants.ARGUMENTS[2].value
            self.second_lang = constants.ARGUMENTS[3].value
            debug("set a langs for history")


    def set_text( self, text ):

        self.text = text
        debug( f"set a text for history: { text }" )
    

    def set_text_trans( self, text ):

        self.text_trans = text
        debug( f"set a text_trans for history: { text }" )


    def set_first_lang( self, lang ):

        self.first_lang = lang
        debug( f"set a f_lang for history: { lang }" )


    def set_second_lang( self, lang ):

        self.second_lang = lang
        debug( f"set a s_lang for history: { lang }" )
