import sys, os
from . import constants

class Prints:

    def print_informations( self ):
        print( "Google translator (googletrans==4.0.0-rc1)" )


    def print_helps( self ):

        print( "| Functions for manipulating this an app." )
        print( "|" )
        print(f"| {'exit()' : <10} For exited this app.")
        print(f"| {'clear()' : <10} For clearing all a texts.")
        print(f"| {'open()' : <10} For opening a web google translator, with return an history word.")
        print(f"| {'value()' : <10} For opening a web google, with return an translated history word.")
        print(f"| {'images()' : <10} For opening a web google images, with return an history word.")


    def print_nots_value( self ):

        print( f"{ constants.ERROR_ICON } This a word not's value." )
    

    def print_error( self ):

        self.print_trans( f"{ constants.ERROR_ICON } This a word, not's exist in the google, in a list words." )


    def print_loading( self ):
        sys.stdout.write( constants.LOADING );
        sys.stdout.flush()


    def print_trans( self, text ):
        print( constants.LAST_LINE + text )
    

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
            arguments = f'{ argument.get_short() }, { argument.get_long() }'
            print(f"{ arguments : <30}{argument.message}")