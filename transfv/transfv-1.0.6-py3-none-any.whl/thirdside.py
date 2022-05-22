from . import constants
import webbrowser
import transfv

class ThirdSide:

    def open_google( self ):

        if ( transfv.translator.history.second_lang != constants.CS_NAME ):
            return True  # Just end this a method, and continue function for print a message.

        uri = self.get_uri_google( f"{ transfv.translator.history.text_trans }+v%C3%BDznam" )
        webbrowser.open( uri )
        return False
    
    def open_google_images( self ):

        arg = "&tbm=isch"
        uri = self.get_uri_google( transfv.translator.history.text, arg )
        webbrowser.open( uri )


    def open_google_trans( self ):

        uri = self.get_uri_google_trans()
        webbrowser.open( uri )


    def get_uri_google_trans( self ):

        transfv.translator.history.set_langs()

        text = transfv.translator.history.text
        if not text:
            text = ""

        return f"{ constants.URI_GOOGLE_TRANS }?sl={ transfv.translator.history.first_lang }&tl={ transfv.translator.history.second_lang }&text={ text }&op=translate"
    

    def get_uri_google( self, text = "", args = "" ):

        return f"https://www.google.com/search?q={ text }{ args }"