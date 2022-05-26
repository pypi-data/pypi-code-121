
#####################################################################
#
# s_db.py
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

import os
import sys
import json
import time
import platform
import hashlib
import sqlite3
from pathlib import Path

from . import s_log , s_config , s_util

#####################################################################

def setup( ) :
    s_log.write( "setup" )
    filedir_create( )

#####################################################################

def reset( ) :
    filepath_delete( )
    
def fsize( ) :
    fp = filepath_get( )

    fs = os.path.getsize( fp )

    return( fs )
    #os.path.getsize( fp )

def fsize_limited( ) :
    fs=fsize()
    if( fs > 20971520 ) :
        s_log.write(fs)
        return( True )
    return(False)

def db_stash( ) :

    curr_fp = filepath_get( )
    new_fp = curr_fp + "-STASH"
    os.rename( curr_fp , new_fp )
    
    data = {
        "curr_fp":curr_fp,
        "new_fp":new_fp
    }

    return( s_util.json_encode( data ) )

def db_unstash( data_json ) :
    data = s_util.json_loads( data_json )
    os.rename( data[ "new_fp" ] , data[ "curr_fp" ] )

#####################################################################

def filedir_create( ) :
    os.makedirs( filedir_get( ) , exist_ok = True )

def filedir_get( ) :
    dbworkspacedir = os.path.join( s_config.get_key( "sys/workspacedir" , "/tmp/sapiadapter" ) + "/db" , "" )
    return( dbworkspacedir )

#####################################################################

def filepath_get( ) :
    tid = str( s_util.thread_get_id( ) )
    fn = s_config.get_key( "/config/session" ) + "-" + tid + ".db"
    #s_log.write(fn)
    fp = filedir_get( ) + fn
    if not os.path.isfile( fp ) :
        dbcon = sqlite3.connect( fp )
        dbcon.commit( )
        dbcon.close( )
        init_schema( )
        init_data( )
    return( fp )

def filepath_delete( ) :
    fp = filepath_get( )
    if os.path.isfile( fp ) :
        os.remove( fp )

def filepath_delete_all( ) :
    for f in os.scandir( filedir_get( ) ) :
        os.remove( f.path )

#####################################################################

def sql_execute( sql , params_tuple = False ) :

    #s_log.write( sql )

    dbcon = sqlite3.connect( filepath_get( ) )
    cur = dbcon.cursor( )
    if params_tuple == False:
        cur.execute( sql )
    else:
        cur.execute( sql , params_tuple )
    dbcon.commit( )
    dbcon.close( )
    cur = False
    dbcon = False

def sql_execute_fetch( sql , fetch_all=False) :

    #s_log.write( sql )

    dbcon = sqlite3.connect( filepath_get( ) )
    dbcon.row_factory = lambda C , R : { c[ 0 ] : R[ i ] for i , c in enumerate( C.description ) }
    cur = dbcon.cursor( )
    cur.execute( sql )

    if fetch_all : 
        rows = cur.fetchall( )
        dbcon.close( )
        cur = False
        dbcon = False
        return( rows )
    else :
        row = cur.fetchone( )
        dbcon.close( )
        cur = False
        dbcon = False
        if( not row ) : return( False )
        return( row )

#####################################################################


def flush( ) :

    # FIXME TODO Maybe delete file?

    table_truncate( "files" ) 
    table_truncate( "env" ) 
    table_truncate( "stdio" ) 
    table_truncate( "args" ) 
    table_truncate( "stacks" ) 
    table_truncate( "meta" ) 
    table_truncate( "templates" ) 

def init_data( ) :
# FIXME TODO add host environment vars e.g. hostname/machine id etc.
    sys_create( "ver_db" , "1.0" )
    sys_create( "ver_sapi" , s_config.get_key( "/config/version" ) )
    sys_create( "serial" , "ODS042e1919c5bd8f41cd8e1a2b8e455dd8f6fb00df0c3916d1137047a7aafc4c42" )
    sys_create( "motto" , "HORAS NON NUMERO NISI SERENAS" )
    sys_create( "rev" , 1 )
    #sys_create( "sys_platform" , sys.platform )
    #sys_create( "sys_version" , sys.version )
    sys_create( "traceid" , s_log.get_traceid( ) )
    sys_create( "time_isoformat" , s_util.time_getisoformat( ) )
    sys_create( "tcreate" , time.time( ) )
    sys_create( "platform_uname" , platform.uname( ) )
    sys_create( "python_version" , platform.python_version( ) )

    sys_create( "config_dbpassthru" , s_config.get_key( "db/passthru" ) )

    #s_log.write(sys_read("time_isoformat"))

def file_contents( ) :


    dbfp = filepath_get( )
    if not os.path.isfile( dbfp ) :
        s_log.write( dbfp + " NOT exists!" )
        return( False )

    with open( dbfp , mode = "rb" ) as file : 
        db_filecontents = file.read( )


    return( db_filecontents )


def blob_set( d ) :
    blob = s_util.decompress( d )
    rewrite( blob )

def blob_get( ) :
    db_filecontents = file_contents( )
    blob = s_util.compress( db_filecontents )
    return( blob )

def rewrite( payload ) :

    if( len( payload ) == 0 ) :
        s_log.write( "ERROR payload empty??")

    # FIXME TODO technically only the filepath is required - no need to create and init db file
    dbfp = filepath_get( )
    with open( dbfp , "wb" ) as file:
        file.write( payload )


    ################################################################

    ver_sapi = sys_read( "ver_sapi" )
    ver_db = sys_read( "ver_db" )

    if( ver_sapi != s_config.get_key( "/config/version" ) ) :
        #s_log.write( "WARNING,VER_SAPI MISMATCH," + ver_sapi + "!=" + s_config.get_key( "/config/version" ) + "," + ver_db )
        s_log.write( "WARNING, VERSION MISMATCH," )

#####################################################################

def table_readall( t , extra = "" ) :
    sql = "SELECT * FROM " + t + " " + extra
    rows = sql_execute_fetch( sql , fetch_all = True )
    return( rows )

def table_truncate( t , extra = "" ) :
    sql = "DELETE from " + t + " " + extra
    sql_execute( sql )

def table_rowcount( t , extra = "") :
    sql = "SELECT COUNT(*) as count FROM " + t + " " + extra
    row = sql_execute_fetch( sql )
    return( row[ "count" ] )

def tablerow_exists( t , extra = "" ) :
    row_count = table_rowcount( t , extra ) 
    if(row_count>0): return(True)
    return(False)

#####################################################################

def init_schema( ) :

    sql_execute( "CREATE TABLE sys ( sn text UNIQUE , sv text )" )
    sql_execute( "CREATE INDEX index_sys ON sys ( sn )" )

    ################################################################

    sql_execute( "CREATE TABLE files ( fp text UNIQUE , fc blob , fs integer , fh text , fm integer )" )
    sql_execute( "CREATE INDEX index_files ON files ( fp )" )

    ################################################################

    sql_execute( "CREATE TABLE env ( eid integer PRIMARY KEY AUTOINCREMENT , en text UNIQUE , ev text )" )
    sql_execute( "CREATE INDEX index_env ON env ( eid , en )" )

    ################################################################

    sql_execute( "CREATE TABLE stdio ( sid integer PRIMARY KEY AUTOINCREMENT , sk integer , sv text )" )
    sql_execute( "CREATE INDEX index_stdio ON stdio ( sid , sk )" )

    ################################################################

    sql_execute( "CREATE TABLE args ( aid integer PRIMARY KEY AUTOINCREMENT , av text )" )
    sql_execute( "CREATE INDEX index_args ON args ( aid )" )

    ################################################################

    sql_execute( "CREATE TABLE stacks ( sid integer PRIMARY KEY AUTOINCREMENT , sk integer , sv text )" )
    sql_execute( "CREATE INDEX index_stacks ON stacks ( sid , sk )" )

    ################################################################

    sql_execute( "CREATE TABLE meta ( mn text UNIQUE , mv text )" )
    sql_execute( "CREATE INDEX index_meta ON meta ( mn )" )

    ################################################################

    sql_execute( "CREATE TABLE templates ( tid integer PRIMARY KEY AUTOINCREMENT , tp text , tk text , tv text )" )
    sql_execute( "CREATE INDEX index_templates ON templates ( tid , tp )" )

#####################################################################

def sys_create( sn , sv_in ) :

    sv = s_util.json_encode( sv_in )

    sql = "INSERT INTO sys( sn , sv ) VALUES ( ? , ? )"
    data = ( sn , sv )
    sql_execute( sql , data )
    return( True )

def sys_count( ) :
    count = table_rowcount( "sys" )
    return( count )

def sys_read( sn ) :

    sql = "SELECT * FROM sys where sn='" + sn + "' limit 1"
    row = sql_execute_fetch( sql )
    if( not row ) : return( False )
    return( json.loads( row[ "sv" ] )  )

def sys_readall( ) :
    rows = table_readall( "sys" )
    return( rows )

def sys_update( sn , sv_in ) :
    sv = s_util.json_encode( sv_in )
    sql = "UPDATE sys SET sv=? where sn=?"
    data = ( sv , sn )
    sql_execute( sql , data )

def sys_delete( sn ) :

    sql = "DELETE FROM sys where sn='" + sn + "'"
    sql_execute( sql )
    return( True )

def sys_deleteall( ) :
    table_truncate( "sys" )

def sys_rev_inc( ) :
    newrev = sys_read( "rev" ) + 1
    sys_update( "rev" , newrev )

####################################################################

def stacks_create( sv_data , sk = 0 ) :

    sv = s_util.json_encode( sv_data )

    sql = "INSERT INTO stacks ( sid , sk , sv ) VALUES ( ? , ? , ? )"
    data = ( None , sk,sv )

    sql_execute( sql , data )
    return( True )

def stacks_count( sk = 0 ) :

    extra = "where sk=" + str( sk )
    count = table_rowcount( "stacks" , extra )
    return( count )

def stacks_read( sk = 0 ) :

    sql = "SELECT * FROM stacks where sk=" + str( sk ) + " order by sid desc" 
    rows = sql_execute_fetch( sql , fetch_all=True)
    return( rows )

def stacks_readall( ) :
    rows = table_readall( "stacks" , extra = "order by sid asc" )
    return( rows )

def stacks_update( sid , sk , sv_data ) :
    sv = s_util.json_encode( sv_data )
    sql = "UPDATE stacks SET sk=? , sv=? where sid=?"
    data = ( sk , sv , sid )
    sql_execute( sql , data )

def stacks_delete( sk = 0 ) :
    sql = "DELETE FROM stacks where sk=" + str( sk ) 
    sql_execute( sql )
    return( True )

# FIXME TODO finish when specific sk is given
def stacks_deleteall( sk = False ) :
    if( sk == False ) :
        table_truncate( "stacks" )
    else:
        pass
    return(True)

def stacks_pop( sk = 0 ) :

    sql = "SELECT * FROM stacks where sk=" + str( sk ) + " order by sid desc limit 1" 
    rows = sql_execute_fetch( sql ,fetch_all=True)

    if( len( rows ) != 1 ) :
        return( False )

    row = rows[ 0 ]
   
    sid = row[ "sid" ]
    sv_dict = json.loads( row[ "sv" ] )

    sql = "DELETE FROM stacks where sid=" + str( sid ) 
    sql_execute( sql )

    return( sv_dict )    


#####################################################################

def env_create( en , ev ) :

    sql = "INSERT INTO env ( eid , en , ev ) VALUES ( null , ? , ? )"
    data = ( en , ev )
    sql_execute( sql , data )
    return(True)

def env_count( ) :
    count = table_rowcount( "env" )
    return( count )

def env_read( en ) :

    sql = "SELECT * FROM env where en='" + en + "' limit 1"
    row = sql_execute_fetch( sql )
    return( row )

def env_readall( ) :
    rows = table_readall( "env" , "order by eid asc")
    return( rows )

def env_update( en , ev ) :
    sql = "UPDATE env SET ev=? where en=?"
    data = ( ev , en )
    sql_execute( sql , data )

def env_delete( en ) :

    sql = "DELETE FROM env where en='" + en + "'"
    sql_execute( sql )
    return( True )

def env_deleteall( ) :
    table_truncate( "env" )

#####################################################################

def meta_create( mn , mv_in ) :

    # FIXME TODO something better?
    meta_delete( mn )

    mv = s_util.json_encode( mv_in )

    sql = "INSERT INTO meta ( mn , mv ) VALUES ( ? , ? )"
    data = ( mn , mv )
    sql_execute( sql , data )
    return(True)

def meta_count( ) :
    count = table_rowcount( "meta" )
    return( count )


def meta_read( mn , raw = False ) :

    sql = "SELECT * FROM meta where mn='" + mn + "' limit 1"
    row = sql_execute_fetch( sql )
    if( not row ) : return( False )
    if(raw):
        return( row[ "mv" ] )
    else:
        return( json.loads( row[ "mv" ] ) )

def meta_readall( ) :
    rows = table_readall( "meta" )
    return( rows )

def meta_update( mn , mv_in ) :
    mv = s_util.json_encode( mv_in )
    sql = "UPDATE meta SET mv=? where mn=?"
    data = ( mv , mn )
    sql_execute( sql , data )

def meta_delete( mn ) :

    sql = "DELETE FROM meta where mn='" + mn + "'"
    sql_execute( sql )
    return( True )

def meta_deleteall( ) :
    table_truncate( "meta" )

def meta_createorupdate( mn , mv ) :
    t = meta_read( mn )
    if t :
        meta_update( mn , mv )
    else :
        meta_create( mn , mv )


####################################################################

def args_create( av ) :

    sql = "INSERT INTO args ( aid , av ) VALUES ( ? , ? )"
    data = ( None , av )
    sql_execute( sql , data )
    return( True )

def args_count( ) :
    count = table_rowcount( "args" )
    return( count )

def args_read( aid ) :

    sql = "SELECT * FROM args where aid=" + aid + " limit 1"
    row = sql_execute_fetch( sql )
    return( row )

def args_readall( ) :
    rows = table_readall( "args" , "order by aid asc")
    return( rows )

def args_update( aid , av ) :
    sql = "UPDATE args SET av=? where aid=?"
    data = ( av , aid )
    sql_execute( sql , data )

def args_delete( aid ) :

    sql = "DELETE FROM args where aid=" + aid 
    sql_execute( sql )
    return( True )

def args_deleteall( ) :
    table_truncate( "args" )

####################################################################

# stdin 0 , stdout 1 , stderr 2
def stdio_create( sk , sv ) :
    sql = "INSERT INTO stdio ( sid , sk , sv ) VALUES ( null , ? , ? )"
    data = ( sk , sv )
    sql_execute( sql , data )
    return( True )

def stdio_count( sk ) :
    count = table_rowcount( "stdio" , "where sk=" + str( sk ) )
    return( count )

def stdio_read( sk ) :
    sql = "SELECT * FROM stdio where sk=" + str( sk ) + " order by sid asc" 
    rows = sql_execute_fetch( sql ,fetch_all=True)
    return( rows )

def stdio_readformatted( sk ) :
    rows = stdio_read( sk )
    buff = ""
    for r in rows:
        #buff = buff + str( r["sv"],"utf-8")+"\n"
        buff = buff + r["sv"]+"\n"
    return( buff )

def stdio_readall( ) :
    rows = table_readall( "stdio" )
    return( rows )

def stdio_update( sid , sk , sv ) :
    sql = "UPDATE stdio SET sk=? , sv=? where sid=?"
    data = ( sk , sv , sid )
    sql_execute( sql , data )

def stdio_delete( sk = 0 ) :

    sql = "DELETE FROM stdio where sk = " + str( sk ) 
    sql_execute( sql )

    return( True )    

def stdio_deleteall( ) :
    table_truncate( "stdio" )

def stdio_has_stderr( ) :

    if( stdio_count( 2 ) > 0 ) :
        return( True )

    return( False )

def stdio_get_stderr( ) :
    return( stdio_readformatted( 2 ) )

def stdio_get_stdout( ) :
    return( stdio_readformatted( 1 ) )

####################################################################

def files_create( fp , trimpath = "" ) :

    # FIXME TODO have some restriction paths allowed - this breaks when creating UID directories for work spaces
    # FIXME TODO add tests for this...
    #if( s_util.pathnotallowed( fp ) ) : return( False )

    ####################################################################

    if not os.path.isfile( fp ) :
        s_log.write( fp + " NOT found!" )
        return( False )

    fs = os.path.getsize( fp )

    with open( fp , mode = "rb" ) as file : 
        fc = file.read( )


    # FIXME TODO use better hash lib blake2b?
    fh = hashlib.md5( fc ).hexdigest( )

    ####################################################################

    fp_processed = fp

    if( trimpath != "" ) :
        fp_processed = fp[len(trimpath ):]


    statinfo = os.stat( fp )

    ####################################################################

    sql = "INSERT INTO files ( fp , fc , fs , fh , fm ) VALUES (?, ?, ?, ?,?)"
    data_tuple = ( fp_processed , fc , fs , fh , statinfo.st_mtime)

    sql_execute( sql , data_tuple )

    return( True )

def files_count( ) :
    count = table_rowcount( "files" )
    return( count )

def files_read( fp ) :

    sql =  "SELECT * FROM files where fp='" + fp + "' limit 1" 
    row = sql_execute_fetch( sql )
    return( row )

def files_readall( ) :
    rows = table_readall( "files" )
    return( rows )

# FIXME TODO def files_update !!!
# Delete current path and create a new one?!?!?!
def files_update( fp ) :
    files_delete( fp ) 
    return( files_create( fp ) )

def files_delete( fp ) :

    sql = "DELETE FROM files where fp='" + fp + "'"
    sql_execute( sql )

    return( True )  

def files_deleteall( ) :
    table_truncate( "files" )

def files_dict2json( fp , fdict ) :

    #if( s_util.pathnotallowed( fp ) ) : return( False )

    fc = s_util.json_encode( fdict )

    fs = len( fc )
    fh = hashlib.md5( fc.encode( "utf-8" ) ).hexdigest( )

    fm = s_util.time_now( )

    sql = "INSERT INTO files ( fp , fc , fs , fh ,fm) VALUES (?, ?, ?, ?,?)"
    data_tuple = ( fp , fc , fs , fh ,fm)
    sql_execute( sql , data_tuple )

    return( True )

def files_getcontent( fp ) :
    f = files_read( fp )
    if not f :
        s_log.write( "False files_getcontent" )
        return( False )
    return( f[ "fc" ] )

def files_readallmeta( ) :

    sql = "SELECT fp,fs,fh,fm FROM files" 
    rows = sql_execute_fetch( sql , fetch_all = True )
    return( rows )

def files_write( fp_source , fp_target = False ) :

    if( fp_target == False ) :
        fp_target = fp_source

    fd = files_read( fp_source )

    fp_target_tmp = fp_target + s_util.uhash( )

    with open( fp_target_tmp , "wb" ) as f :
        f.write( fd[ "fc" ] )

    s_util.file_replace( fp_target_tmp , fp_target )

    s_util.file_settimes( fp_target , fd[ "fm" ] )


# with open( dir_cache + "local_out.png" , "wb" ) as f :
#def files_write( fp ) :
#    # FIXME TODO test this... with open( dir_cache + "local_out.png" , "wb" ) as f :
#    with open( fp , "w" , 1 ) as f :
#        f.write( files_getcontent( fp ) )

def files_restore( rpath = False ) :
    db_files = files_readallmeta( )
    s_log.write(db_files)
    for db_file in db_files :

        fp_source = db_file[ "fp" ]

        if(rpath!=False):
            # FIXME TODO WARNING this removes "chars"!
            fp_target=rpath.rstrip("/")+ "/" + fp_source
        else:
            fp_target=fp_source

        #s_log.write(fp_source+" -> "+fp_target)

        dp = s_util.path_dirname( fp_target )
        #print(dp)
        dp_path = Path( dp )
        dp_path.mkdir( parents = True , exist_ok = True )


        files_write( fp_source,fp_target)

#        with open( fp_target , "wb" ) as f :
#            f.write( files_getcontent( fp_source ) )

#        s_util.file_settimes(fp_target,db_file["fm"])

def files_createall( pat ) :
    # Let's be clever and try to trim the pattern matching directory...

    # FIXME TODO be careful... we are only checking for wildcard "**"
    # FIXME TODO WARNING this removes "chars"!
    pat_trim = pat.rstrip( "**" )
    if( pat_trim == pat ) :
        pat_trim = ""

    files = s_util.glob_files( pat , True )
    for f in files :
        if os.path.isfile( f ) :
            files_create( f , pat_trim )



####################################################################

def templates_create( tp , tk , tv ) :
    if( s_util.pathnotallowed( tp ) ) : return( False )
    sql = "INSERT INTO templates ( tp,tk,tv) VALUES ( ? , ? , ? )"
    data = ( tp , tk , tv )
    sql_execute( sql , data )
    return(True)

def templates_count( ) :
    count = table_rowcount( "templates" )
    return( count )

def templates_read( tp ) :
    sql = "SELECT * FROM templates where tp='" + tp + "' order by tid asc" 
    rows = sql_execute_fetch( sql ,fetch_all=True)
    return( rows ) 

def templates_readall( ) :
    rows = table_readall( "templates" )
    return( rows )    

def templates_update( tp , tk , tv ) :
    sql = "UPDATE templates SET tk=? , tv=? where tp=?"
    data = ( tk , tv , tp )
    sql_execute( sql , data )

def templates_delete( tp ) :

    sql = "DELETE FROM templates where tp='" + tp + "'"
    sql_execute( sql )
    return( True )

def templates_deleteall( ) :
    table_truncate( "templates" )

