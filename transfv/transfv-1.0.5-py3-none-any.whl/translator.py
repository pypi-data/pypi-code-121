from . import constants
import transfv
import googletrans

class Translator:
    
    def __init__( self ):
        self.dest = constants.FIRST_LANG
        self.translator = googletrans.Translator()


    def translation_loop( self ):

        while( True ):

            text = input( constants.INPUT )

            if transfv.checkFunction( text ):
                continue

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
            translate = constants.ERROR_MESSAGE

        transfv.prints.print_trans( translate )


    def detectDect( self, text ):

        dest = self.translator.detect( text ).lang

        first = constants.ARGUMENTS[2]
        second = constants.ARGUMENTS[3]

        if ( dest == first.value ):
            dest = second.value
        elif ( dest == second.value ):
            dest = first.value
        
        return dest
