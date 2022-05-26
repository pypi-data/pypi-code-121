
#####################################################################
#
# s_cleanup.py
#
# Project   : SAPIADAPTER
# Author(s) : Zafar Iqbal < zaf@sparc.space >
# Copyright : (C) 2022 SPARC PC < https://sparc.space/ >
#
# All rights reserved. No warranty, explicit or implicit, provided.
# SPARC PC is and remains the owner of all titles, rights
# and interests in the Software.
#
#####################################################################

import atexit

#####################################################################

from . import s_log , s_db

#####################################################################

def cleanup( ) :
    # FIXME TODO only delete the threads db! otherwise another process could be still running! not all
    # FIXME TOOD count how db files are in dir and report back!
    s_db.filepath_delete( )
    #s_log.write( "cleanup" )
    pass

#####################################################################

atexit.register( cleanup )
    