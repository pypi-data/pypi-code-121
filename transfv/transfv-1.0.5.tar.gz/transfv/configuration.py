import pathlib
from . import constants
import configparser

class Configuration:

    def __init__( self ):

        self.config = configparser.ConfigParser()
        self.file_read = None
        self.open_config()


    def get_path_file( self ):
        dir = pathlib.Path(__file__).parent
        return (dir / constants.SETTINGS_FILE )


    def open_config( self ):
        self.file_read = self.config.read( self.get_path_file() )


    def write_config( self ):
        with open( self.get_path_file(), 'w+' ) as configfile:
            self.config.write(configfile)


    def has_langs_section( self ):
        return self.config.has_section( constants.LANGUAGE_NAME )


    def has_lang_option( self, option ):

        if not self.has_langs_section():
            self.config[ constants.LANGUAGE_NAME ] = {}

        return self.config.has_option( constants.LANGUAGE_NAME, option )


    def get_lang_config( self, option ):

        if self.has_lang_option( option ):
            return self.config.get( constants.LANGUAGE_NAME, option )
        
        return None
    

    def set_lang_config( self, option, value ):

        if self.has_lang_option( option ):
            return self.config.set( constants.LANGUAGE_NAME, option, value )
        else:
            self.config[ constants.LANGUAGE_NAME ][ option ] = value


    def get_first_lang_config( self ):
        return self.get_lang_config( constants.FIRST_LANG_NAME )


    def get_second_lang_config( self ):
        return self.get_lang_config( constants.SECOND_LANG_NAME )


    def set_first_lang_config( self, value = constants.FIRST_LANG):

        if value == None:
            value = constants.FIRST_LANG

        self.set_lang_config( constants.FIRST_LANG_NAME, value )


    def set_second_lang_config( self, value = None ):

        if value == None:
            value = constants.SECOND_LANG

        self.set_lang_config( constants.SECOND_LANG_NAME, value )
    

    def check_languages( self ):
        
        first = constants.ARGUMENTS[2]
        second = constants.ARGUMENTS[3]
        first_value = first.value
        second_value = second.value

        if self.file_read:

            if not first_value:
                first_value = self.get_first_lang_config()

            if not second_value:
                second_value = self.get_second_lang_config()

            self.set_first_lang_config(first_value)
            self.set_second_lang_config(second_value)
            self.write_config()

        else:

            if not first_value:
                first_value = constants.FIRST_LANG

            if not second_value:
                second_value = constants.SECOND_LANG

            self.set_first_lang_config(first_value)
            self.set_second_lang_config(second_value)
            self.write_config()

        first.set_value( first_value )
        second.set_value( second_value )