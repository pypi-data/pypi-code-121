
#####################################################################
#
# s_cache.py
#
# Project   : SAPIADAPTER
# Author(s) : Zafar Iqbal < zaf@sparc.space >
# Copyright : (C) 2022 SPARC PC < https://sparc.space/ >
#
# All rights reserved. No warranty, explicit or implicit, provided.
# SPARC PC is and remains the owner of all titles, rights
# and interests in the Software.
#
# FIXME TODO - log rotation/retention to not overflow disk space
#
#####################################################################

import os
from . import s_log , s_util 

#####################################################################

# FIXME TODO should be coming from config otherwise default
cache_dirpath = "/tmp/sapiadapter/cache/"

def available_for_inputs( inputs ) :

    # FIXME TODO group duplicated code
    inputs_str = s_util.json_dumps( inputs )
    cache_hash = s_util.hash( inputs_str.encode( "utf-8" ) )
    cache_filepath = cache_dirpath + cache_hash + ".json"
    s_log.write( "cache_filepath=" + cache_filepath )

    return os.path.isfile( cache_filepath ) 

def set_inputoutput( inputs , outputs ) :
    # FIXME TODO group duplicated code
    inputs_str = s_util.json_dumps( inputs )
    cache_hash = s_util.hash( inputs_str.encode( "utf-8" ) )
    cache_filepath = cache_dirpath + cache_hash + ".json"
    if( os.path.isfile( cache_filepath ) ) : return( None )
    init_path( cache_filepath )
    response = outputs.copy( )
    s_util.json_save( cache_filepath , response )
    s_log.write( "cache updated" )

def get_inputoutput( inputs ) :
    # FIXME TODO group duplicated code
    inputs_str = s_util.json_dumps( inputs )
    cache_hash = s_util.hash( inputs_str.encode( "utf-8" ) )
    cache_filepath = cache_dirpath + cache_hash + ".json"
    return( s_util.json_load( cache_filepath ) )

def init_path( fp ) :

    fpdirname = os.path.dirname( fp )

    if( not os.path.isdir( fpdirname ) ) :
        os.makedirs( fpdirname , exist_ok = True )
