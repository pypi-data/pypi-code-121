class Argument:

    def __init__( self, argShort, argLong, message = None ):
        self.short = argShort
        self.long = argLong
        self.message = message
        self.value = None
    

    def get_short( self ):
        return f"-{ self.short }"
    

    def get_long( self ):
        return f"--{ self.long }"
    

    def get_full( self ):
        return ( self.get_short(), self.get_long() )
    

    def set_value( self, value ):
        self.value = value