import sys, os
from . import constants

class Prints:

    def print_informations( self ):

        first = constants.ARGUMENTS[2].value
        second = constants.ARGUMENTS[3].value
        print( f"# Google translator |{ first }/{ second }|" )


    def print_helps( self ):

        print( "┌# Functions for manipulating this an app." )
        print( "│" )
        print(f"│ {constants.EXIT : <10} For exited this app.")
        print(f"│ {constants.CLEAR : <10} For clearing all a texts.")
        print(f"│ {constants.INFO : <10} For get information to this app.")
        print( "│" )
        print(f"╰─╮ {constants.OPEN : <10} For opening an web tab for a google translator.")
        print(f"  │ {constants.OPEN_TWO : <10} For opening an web tabs for a translator and a images.")
        print(f"╭─╯ {constants.OPEN_ALL : <10} For opening an web tabs for a google, a translator and a images.")
        print( "│" )
        print(f"│ {constants.VALUE : <10} For opening an web tab for a goole")
        print(f"│ {constants.IMAGES : <10} For opening an web tab for a images.")
        

    def print_nots_value( self ):

        print( f"{ constants.ERROR_ICON } This a word not's value." )
    

    def print_error( self, message ):

        print( f"{constants.LAST_LINE}{ constants.ERROR_ICON } { message }" )


    def print_loading( self ):
        sys.stdout.write( constants.LOADING );
        sys.stdout.flush()


    def print_trans( self, text, translate ):
        print( constants.LAST_LINE + "   " )
        print( f"╭⁌ { text }" )
        print( f"╰─⁍ { translate }" )
        print()
    

    def print_function( self, text ):
        print( text )
    

    def clear_console( self ):
        command = 'clear'
        if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
            command = 'cls'
        os.system(command)

    
    def clear( self ):
        self.clear_console()

    
    def helper( self ):
        print( f'Usage: { constants.APP } [OPTIONS]\n' )
        print(f"{'Option' : <30}Explanation")
        print(f"{'--------' : <30}-------")
        for argument in constants.ARGUMENTS:

            if argument.get_short() == '-None':
                arguments = argument.get_long()
            else:
                arguments = f'{ argument.get_short() }, { argument.get_long() }'

            if type( argument.message ) == str:
                print(f"{ arguments : <30}{argument.message}")
            else:
                for i in range(len(argument.message)):
                    if i == 0:
                        print(f"{ arguments : <30}{argument.message[i]}")
                    else:
                        print(f"{ '' : <30}{argument.message[i]}")
    

    def debug( self, value ):

        if constants.IS_DEBUG:
            print( f"⚪ { value }")
