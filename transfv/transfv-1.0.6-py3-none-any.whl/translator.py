from . import constants
import transfv
import googletrans

class History:

    def __init__( self ):

        self.text = ""
        self.text_trans = ""
        self.first_lang = ""
        self.second_lang = ""
    

    def set_langs( self ):

        if not self.text:
            self.first_lang = constants.ARGUMENTS[2].value
            self.second_lang = constants.ARGUMENTS[3].value


    def set_text( self, text ):

        self.text = text
    

    def set_text_trans( self, text ):

        self.text_trans = text


    def set_first_lang( self, lang ):

        self.first_lang = lang


    def set_second_lang( self, lang ):

        self.second_lang = lang



class Translator:
    
    def __init__( self ):
        self.dest = constants.FIRST_LANG
        self.translator = googletrans.Translator()
        self.history = History()


    def clear( self ):

        self.history.__init__()


    def translation_loop( self ):

        while( True ):

            text = input( constants.INPUT )

            if transfv.checkFunction( text ):
                continue

            self.history.set_text( text )

            self.translate( text )


    def translate( self, text ):

        if ( not text ):
            return

        transfv.prints.print_loading()

        translate = ""
        try:
            dest = self.detectDect( text )
            translate = self.translator.translate( text, dest=dest ).text
        except:
            self.clear()
            transfv.prints.print_error()
            return

        transfv.prints.print_trans( translate )
        self.history.set_text_trans( translate )


    def detectDect( self, text ):

        dest = self.translator.detect( text ).lang
        self.history.set_first_lang( dest )

        first = constants.ARGUMENTS[2]
        second = constants.ARGUMENTS[3]

        if ( dest == first.value ):
            dest = second.value
        elif ( dest == second.value ):
            dest = first.value

        self.history.set_second_lang( dest )
        
        return dest
