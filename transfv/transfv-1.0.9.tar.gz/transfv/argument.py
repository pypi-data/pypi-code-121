from . import constants

class Argument:

    def __init__( self, argShort, argLong, message, access = 'get', callback = None ):
        self.short = argShort
        self.long = argLong
        self.message = message
        self.value = None
        self.access = access
        self.set_callback( callback )


    def get_short( self ):
        return f"-{ self.short }"
    

    def get_long( self ):
        return f"--{ self.long }"
    

    def get_full( self ):
        return ( self.get_short(), self.get_long() )
    

    def set_value( self, value ):
        self.value = value
    

    def get_short_opt( self ):
        return self.get_opt( constants.SHORT, self.short )
    

    def get_long_opt( self ):
        return self.get_opt( constants.LONG, self.long )


    def get_opt( self, type, arg ):

        opt = ""
        if self.access == constants.GET and arg:
            opt = arg

        elif self.access == constants.SET and arg:
            opt = f"{ arg }{ type }"

        return opt
    

    def set_callback( self, callback ):

        self.callback = callback
        return self


    def emit( self, object, arg ):

        if self.callback:
            self.callback( object, arg )
        else:
            print( "Call back not implement for event." )
