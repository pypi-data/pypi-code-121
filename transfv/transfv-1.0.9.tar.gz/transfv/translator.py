from .obj import get_root
from . import constants
from .history import History

import googletrans

class Translator:
    
    def __init__( self ):
        self.dest = constants.FIRST_LANG
        self.translator = googletrans.Translator()
        self.history = History()
        self.transfv = get_root()


    def clear( self ):

        self.history.__init__()


    def check_more_words( self ):
        rawText = input( constants.INPUT ).split()
        i_last = len( rawText ) - 1

        if i_last == 0:
            self.one_word( rawText )
        elif i_last == -1:
            self.transfv.checkFunction( constants.CLEAR )
        else:
            self.more_words( rawText, i_last )


    def one_word( self, raw_text ):
        text = ' '.join( raw_text )
        if self.transfv.checkFunction( text ):
            return

        self.history.set_text( text )
        self.translate( text )
    

    def more_words( self, raw_text, i_last ):
        text_func = raw_text[ i_last ]

        isHaveFunc = False
        if self.transfv.checkFunction( text_func, False ):

            # Have func
            self.transfv.checkFunction( constants.CLEAR )
            del raw_text[ i_last ]
            isHaveFunc = True

        text = ' '.join( raw_text )
        self.history.set_text( text )
        self.translate( text )

        if isHaveFunc:
            self.transfv.prints.print_function( text_func )
            self.transfv.checkFunction( text_func )


    def translation_loop( self ):

        while( True ):
            self.check_more_words()
    

    def get_translate_online( self, text ):
        dest = self.detectDect( text )
        translate = self.translator.translate( text, dest=dest ).text
        return translate


    def get_translates( self, text ):

        translate = ""
        exist_trans = self.transfv.configuration.languages.get_trans( text )

        if exist_trans:
            translate = exist_trans
        else:
            translate = self.get_translate_online( text )
            self.transfv.configuration.languages.add_data( text, translate )
        
        return translate


    def error( self, e ):
        self.clear()
        message = getattr( e, 'message', str(e) )
        self.transfv.prints.print_error( message )

    def translate( self, text ):

        if ( not text ):
            return

        self.transfv.prints.print_loading()

        translate = ""
        try:
            translate = self.get_translates( text )
        except Exception as e:
            self.error( e )
            return

        self.transfv.prints.print_trans( text, translate )
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
