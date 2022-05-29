from .obj import debug, get_root
from . import constants
import os

class Events:

    def __init__( self ) -> None:
        self.transfv = get_root()


    def help( self, object, arg ):
        self.transfv.helper()


    def message( self, object, arg ):
        object.set_value( arg )

        debug( "set history" )
        self.transfv.translator.history.set_text( arg )
        self.transfv.translator.detectDect( arg )

        debug("translate")
        self.transfv.translator.translate( arg )
        self.transfv.save_translations()


    def first( self, object, arg ):

        if arg == constants.GET:
            print(self.transfv.configuration.get_first_lang_config())
        else:
            object.set_value( arg )
            self.transfv.configuration.check_languages()


    def second( self, object, arg ):

        if arg == constants.GET:
            print(self.transfv.configuration.get_second_lang_config())
        else:
            object.set_value( arg )
            self.transfv.configuration.check_languages()


    def open( self, object, arg ):
        object.set_value( True )

        debug("open translator")
        self.transfv.checkFunction( constants.OPEN )


    def value( self, object, arg ):
        object.set_value( True )

        debug("open value")
        self.transfv.checkFunction( constants.VALUE )


    def images( self, object, arg ):
        object.set_value( True )

        debug("open images")
        self.transfv.checkFunction( constants.IMAGES )
    

    def info( self, object, arg ):
        self.transfv.prints.print_informations()


    def words_db( self, object, arg ):

        if arg == constants.GET:
            print( self.transfv.configuration.languages )
        else:
            os.system( f"{arg} {self.transfv.absolute_path_files( constants.LANGUAGES_FILE )}" )
