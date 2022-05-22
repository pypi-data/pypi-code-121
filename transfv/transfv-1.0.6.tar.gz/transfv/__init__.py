#!/usr/bin/python

import sys, getopt
from . import constants
from .prints import Prints
from .translator import Translator
from .configuration import Configuration
from .thirdside import ThirdSide

prints = Prints()
translator = Translator()
configuration = Configuration()
thirdside = ThirdSide()


def exit_app( value = 0 ):
    sys.exit( value )
    pass


def set_vars_from_args(argv):
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
        exit_app( 2 )

    for opt, arg in opts:
        if opt in help.get_full():
            prints.helper()
            exit_app()
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


def clear():

    prints.clear()
    translator.clear()


def checkFunction( text ):

    if ( text == constants.EXIT ):
        exit_app()
    elif ( text == constants.CLEAR ):
        clear()
        return True
    elif ( text == constants.INFO ):
        prints.print_informations()
        return True
    elif ( text == constants.OPEN ):
        thirdside.open_google_trans()
        return True
    elif ( text == constants.VALUE ):
        if thirdside.open_google():
            prints.print_nots_value()
        return True
    elif ( text == constants.IMAGES ):
        thirdside.open_google_images()
        return True
    elif ( text == constants.HELP ):
        prints.print_helps()
        return True
    
    return False


def main():
    argument = sys.argv[1:]
    set_vars_from_args(argument)
    configuration.check_languages()

    scenario( argument )


def scenario( argument ):

    if ( not argument ):
        prints.print_informations()
        translator.translation_loop()
    else:
        message = constants.ARGUMENTS[1]
        open = constants.ARGUMENTS[4]
        value = constants.ARGUMENTS[5]
        images = constants.ARGUMENTS[6]

        if open.value or value.value or images.value:
            if message.value:
                print( "set history" )
                translator.history.set_text( message.value )
                translator.detectDect( message.value )

        if open.value:
            print("open translator")
            checkFunction( constants.OPEN )
        else:
            print("translate")
            translator.translate( message.value )
        
        if value.value and not open.value:
            print("open value")
            checkFunction( constants.VALUE )
        elif value.value and open.value:
            print(f"{ constants.LAST_LINE }translate")
            translator.translate( message.value )
            print("open value")
            checkFunction( constants.VALUE )
        
        if images.value:
            print("open images")
            checkFunction( constants.IMAGES )
