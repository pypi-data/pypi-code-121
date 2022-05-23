#!/usr/bin/python

import sys, getopt
from . import constants
from .prints import Prints
from .translator import Translator
from .configuration import Configuration
from .thirdside import ThirdSide

class App:

    def __init__( self ):

        self.prints = Prints()
        self.translator = Translator( self )
        self.configuration = Configuration()
        self.thirdside = ThirdSide( self )

        self.prints.debug("init app")


    def exit_app( self, value = 0 ):
        sys.exit( value )
        pass


    def set_vars_from_args( self, argv ):
        help = constants.ARGUMENTS[0]
        message = constants.ARGUMENTS[1]
        first = constants.ARGUMENTS[2]
        second = constants.ARGUMENTS[3]
        open = constants.ARGUMENTS[4]
        value = constants.ARGUMENTS[5]
        images = constants.ARGUMENTS[6]

        try:
            opts, args = getopt.getopt(argv,
            f"{ help.short }{open.short}{value.short}{images.short}{ message.short }:{ first.short }:{ second.short }:",
            [ help.long, {open.long}, {value.long}, {images.long}, f"{ message.long }=", f"{ first.long }=", f"{ second.long }=" ])

        except getopt.GetoptError:
            self.exit_app( 2 )

        for opt, arg in opts:
            if opt in help.get_full():
                prints.helper()
                self.exit_app()
            elif opt in open.get_full():
                open.set_value( True )
            elif opt in value.get_full():
                value.set_value( True )
            elif opt in images.get_full():
                images.set_value( True )
            elif opt in message.get_full():
                message.set_value( arg )
            elif opt in first.get_full():
                first.set_value( arg )
            elif opt in second.get_full():
                second.set_value( arg )


    def clear( self ):

        self.prints.clear()
        self.translator.clear()


    def checkFunction( self, text ):

        if ( text == constants.EXIT ):
            self.exit_app()
        elif ( text == constants.CLEAR ):
            self.clear()
            return True
        elif ( text == constants.INFO ):
            self.prints.print_informations()
            return True
        elif ( text == constants.OPEN ):
            self.thirdside.open_google_trans()
            return True
        elif ( text == constants.VALUE ):
            if self.thirdside.open_google():
                self.prints.print_nots_value()
            return True
        elif ( text == constants.IMAGES ):
            self.thirdside.open_google_images()
            return True
        elif ( text == constants.HELP ):
            self.prints.print_helps()
            return True
        
        return False


    def main( self ):
        argument = sys.argv[1:]
        self.set_vars_from_args(argument)
        self.configuration.check_languages()

        self.scenario( argument )


    def scenario( self, argument ):

        if ( not argument ):
            self.prints.print_informations()
            self.translator.translation_loop()
        else:
            message = constants.ARGUMENTS[1]
            open = constants.ARGUMENTS[4]
            value = constants.ARGUMENTS[5]
            images = constants.ARGUMENTS[6]

            if open.value or value.value or images.value:
                if message.value:
                    self.prints.debug( "set history" )
                    self.translator.history.set_text( message.value )
                    self.translator.detectDect( message.value )

            if open.value:
                self.prints.debug("open translator")
                self.checkFunction( constants.OPEN )
            else:
                self.prints.debug("translate")
                self.translator.translate( message.value )
            
            if value.value and not open.value:
                self.prints.debug("open value")
                self.checkFunction( constants.VALUE )
            elif value.value and open.value:
                self.prints.debug(f"{ constants.LAST_LINE }translate")
                self.translator.translate( message.value )
                self.prints.debug("open value")
                self.checkFunction( constants.VALUE )
            
            if images.value:
                self.prints.debug("open images")
                self.checkFunction( constants.IMAGES )
