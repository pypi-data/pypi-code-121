#!/usr/bin/python

import sys

from .obj import debug
from . import constants
from .prints import Prints
from .translator import Translator
from .configuration import Configuration
from .thirdside import ThirdSide
from .arguments import Arguments

class App:

    def __init__( self ):

        constants.ROOT = self
        self.prints = Prints()
        self.translator = Translator()
        self.configuration = Configuration()
        self.thirdside = ThirdSide()
        self.arguments = Arguments()

        debug("init app")


    def absolute_path_files( self, name ):
        return self.configuration.get_path_file( name )

    def save_translations(self):
        absolute_path = self.absolute_path_files( constants.LANGUAGES_FILE )
        self.configuration.languages.write_file( absolute_path )


    def exit_app( self, value = 0 ):
        self.save_translations()
        sys.exit( value )


    def helper( self ):
        self.prints.helper()
        self.exit_app()


    def clear( self ):

        self.prints.clear()
        self.translator.clear()


    def info( self ):
        self.prints.print_informations()
    

    def open( self ):
        self.thirdside.open_google_trans()
    

    def value( self ):

        if self.thirdside.open_google():
                self.prints.print_nots_value()
    

    def images( self ):
        self.thirdside.open_google_images()

    
    def help( self ):
        self.prints.print_helps()
    

    def lang_detect( self ):

        first = self.translator.history.first_lang
        second = self.translator.history.second_lang

        if first == '' or second == '':
            text = self.translator.history.text
            self.translator.detectDect( text )


    def checkFunction( self, text, isActive = True ):

        if ( text == constants.EXIT ):
            if isActive:
                self.exit_app()
        elif ( text == constants.CLEAR ):
            if isActive:
                self.clear()
                self.info()
            return True
        elif ( text == constants.INFO ):
            if isActive:
                self.info()
            return True
        elif ( text == constants.OPEN ):
            if isActive:
                self.lang_detect()
                self.open()
            return True
        elif ( text == constants.OPEN_ALL ):
            if isActive:
                self.lang_detect()
                self.value()
                self.open()
                self.images()
            return True
        elif ( text == constants.OPEN_TWO ):
            if isActive:
                self.lang_detect()
                self.open()
                self.images()
            return True
        elif ( text == constants.VALUE ):
            if isActive:
                self.lang_detect()
                self.value()
            return True
        elif ( text == constants.IMAGES ):
            if isActive:
                self.images()
            return True
        elif ( text == constants.HELP ):
            if isActive:
                self.help()
            return True
        else:
            # if isActive:
            self.clear()
            self.info()
        
        return False


    def main( self ):
        self.configuration.check_languages()
        self.arguments.set_vars_from_args()

        self.scenario( self.arguments.argument )


    def scenario( self, argument ):

        if ( not argument ):
            self.prints.print_informations()
            self.translator.translation_loop()
