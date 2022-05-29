import sys, getopt

from .obj import debug, get_root
from . import constants
from .events import Events


class Arguments:

    def __init__( self ) -> None:
        self.transfv = get_root()
        self.argument = sys.argv[1:]
        self.events = Events()

        self.arguments = [
            constants.ARGUMENTS[0].set_callback( self.events.help ),
            constants.ARGUMENTS[1].set_callback( self.events.message ),
            constants.ARGUMENTS[2].set_callback( self.events.first ),
            constants.ARGUMENTS[3].set_callback( self.events.second ),
            constants.ARGUMENTS[4].set_callback( self.events.open ),
            constants.ARGUMENTS[5].set_callback( self.events.value ),
            constants.ARGUMENTS[6].set_callback( self.events.images ),
            constants.ARGUMENTS[7].set_callback( self.events.info ),
            constants.ARGUMENTS[8].set_callback( self.events.words_db ),
        ]


    def get_short_arguments( self ):

        opts = ""
        for argument in self.arguments:

            # print(argument.get_short_opt())
            opts += argument.get_short_opt()
        
        return opts

    def get_long_arguments( self ):

        opts = []
        for argument in self.arguments:
            
            opt = argument.get_long_opt()

            if opt:
                opts.append( opt )

        return opts


    def set_vars_from_args( self ):

        try:
            short_arguments = self.get_short_arguments()
            long_argument = self.get_long_arguments()
            opts, args = getopt.getopt( self.argument,
            short_arguments,
            long_argument )

            debug( f"short args: { short_arguments }" )
            debug( f"long args: { long_argument }" )
    
        except getopt.GetoptError:
            self.transfv.exit_app( 2 )

        for opt, arg in opts:
            for argument in self.arguments:

                if opt in argument.get_full():
                    argument.emit( argument, arg )
