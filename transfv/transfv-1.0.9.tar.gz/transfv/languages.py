from . import constants
import json

class Languages:

    def __init__(self) -> None:
        self.fcc_data = None
    

    def open_file(self, name):
        try:
            with open(name, 'r', encoding=constants.ENCODING) as fcc_file:
                fcc_data = json.load( fcc_file )
                self.set_data( fcc_data )
                return fcc_data
        except:
            self.set_data( { } )
            return self.fcc_data


    def write_file( self, name ):
        with open( name, 'w+', encoding=constants.ENCODING ) as fcc_file:
            json.dump( self.fcc_data, fcc_file, indent=constants.INDENT )


    def set_data(self, data):
        self.fcc_data = data
    

    def add_data( self, key, value ):
        self.fcc_data[ key.lower() ] = value.lower()
    

    def get_trans( self, input ):
        for key in self.fcc_data:
            translation = self.get_exist_trans( key, self.fcc_data, input )

            if translation:
                return translation
        
        return None


    def get_exist_trans( self, key, data, input ):
        first = key.lower()
        second = data[ key ].lower()
        input = input.lower()

        if input == first:
            return second
        elif input == second:
            return first
        
        return None


    def __str__(self) -> str:
        return json.dumps( self.fcc_data, indent=constants.INDENT )