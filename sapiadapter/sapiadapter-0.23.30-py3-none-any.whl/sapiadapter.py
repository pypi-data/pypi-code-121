
#####################################################################
#
# sapiadapter.py
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

import importlib
import multiprocessing
from multiprocessing import Process
from . import s_log , s_config , s_net , s_util , s_db , s_cache , s_cleanup 

#####################################################################

#s_log.write( "    ####    ####    ####    ####\n" )

#####################################################################

s_config.setup( )
s_db.setup( )


#s_log.write( s_config.get_key( "/config/version" ) ) 

#####################################################################

def isready( ) :

    if( not s_util.ready( ) ) :
        s_log.write( "ERROR False ready" )
        return( False )

    #s_log.write( "OK" )
    return( True )

#####################################################################

def config_load_from_file( cp ) :
    return( s_config.load_from_file( cp ) )

def prexit( msg ) :
    s_util.printexit( msg )

def exitiferror( ) :
    if( geterror( ) ) :
        prexit( geterror( ) )

def defdata( raw=False ) :
    return( s_db.meta_read( "_data" , raw ) )

def defmeta( raw=False) :
    return( s_db.meta_read( "_meta" , raw ) )

def geterror( ) :
    return( s_db.meta_read( "_error" ) )

def flush( ) :
    return( s_db.flush( ) )

def reset( ) :
    return( s_db.reset( ) )

def uptime( ) :
    return( s_util.uptime( ) )
def uptime_lap( ) :
    return( s_util.uptime_lap( ) )
def log_lap( ) :
    s_log.write( s_util.uptime_lap( ) )

def heartbeat( t = 60 ) :
    return( s_util.heartbeat( t ) )

def server( runner , debug_errorprexit = False ) :

    s_log.write( "SERVER START" )

    while True :

        s_log.write( "SERVER LOOP" )

        heartbeat( )

        #####################################################

        try :
            flag_jobget = s_net.job_get( )
        except Exception as e :
            s_log.write( "Exception job_get" )
            s_util.printexception( )
            # FIXME TODO add flags to server
            if debug_errorprexit : prexit( "EXCEPTION job_get" )
            print( "Exception job_get" )
            continue
            #sys.exit( 99 )

        #####################################################
        
        if flag_jobget == False :

            #s_config.get_key( "endpoint/url" ) 
            s_log.write( "ERROR False job_get" )
            if debug_errorprexit : prexit( "ERROR False job_get" )
            print( "ERROR False job_get" )
            s_util.sleep( 10 )
            continue

        if flag_jobget == None :
            continue

        #####################################################
        #context =  s_config.get_key( "header_context" )
        #s_log.write( context )
        #qparams = context[ "qparams" ]
        #####################################################


        #if( not s_util.proc_setup( ) ) :
        #    continue

        #####################################################

        #s_util.proc_run( )

        #####################################################

        #s_util.proc_storage( )
        #s_util.proc_teardown( )

        #####################################################

        #config = { 
        #    "_env" : s_util.container_appenvstatic_get( )
        #}
        runner_output = runner( )
        s_db.meta_create( "_runner_exitflag" , runner_output )

        s_net.job_set( )

        #####################################################

        s_log.write( "OK" )

    s_log.write( "SERVER END" )



#####################################################################################################
runner_omnibus_ctime = 0
# Required to make module name scope available in function for importlib
_sapi_runner_omnibus = None
def sapirunner_omnibus_reloadifchanged( path_runner ) :
    global runner_omnibus_ctime
    try :
        if( s_util.file_changed( path_runner , runner_omnibus_ctime ) ) :
            runner_omnibus_ctime = s_util.file_ctime( path_runner )
            importlib.reload( _sapi_runner_omnibus )
            s_log.write( "path_runner RELOAD" , consoleprint = True )
            s_util.sleep( 3 )

    except Exception as e :
        s_log.write( "ERROR sapirunner_omnibus_reloadifchanged " + str( e ) , consoleprint = True )
        s_util.sleep( 3 )
        return( False )

    return( True )


def runner_omnibus( path_runner ) :

    # Required to make module name scope available in function for importlib
    global _sapi_runner_omnibus

    ###############################################################################
    # _CONTAINER_LOCAL_APPSAPIENABLED

    env_appsapienabled = s_util.environ_get("_CONTAINER_LOCAL_APPSAPIENABLED")
    #if( env_appsapienabled == None ) :
    #    s_log.write("_CONTAINER_LOCAL_APPSAPIENABLED NONE DISABLED")
    #    s_util.idle( )

    if( env_appsapienabled and env_appsapienabled.endswith( "_APPSAPIENABLED_" ) ) :
        s_log.write("_CONTAINER_LOCAL_APPSAPIENABLED ENDSWITH DISABLED")
        s_util.idle( )

    ###############################################################################

    s_log.write( "RUNNER_OMNIBUS START " + path_runner )

    if( not s_util.sys_path_append_fp( path_runner ) ) :
        s_log.write( "ERROR NOT FOUND " + path_runner , consoleprint = True )
        prexit( "ERR" )

    import _sapi_runner_omnibus

    global runner_omnibus_ctime
    runner_omnibus_ctime = s_util.file_ctime( path_runner )

    while True :

        s_log.write( "SERVER LOOP" )

        heartbeat( )

        #####################################################
        if( not sapirunner_omnibus_reloadifchanged( path_runner ) ) : continue
        #####################################################

        try :
            flag_jobget = s_net.job_get( )
        except Exception as e :
            s_log.write( "Exception job_get" , consoleprint = True )
            s_util.printexception( )
            continue

        #####################################################
        
        if flag_jobget == False :
            s_log.write( "ERROR False job_get" , consoleprint = True )
            s_util.sleep( 10 )
            continue

        if flag_jobget == None :
            continue

        #####################################################

        # FIXME TODO add try catch

        runner_exitcode = -999

        try :
           
            #runner_exitcode = _sapi_runner_omnibus._entrypoint( )

            ########################################################

            # This could change if runner does a sapi request!?!?
            jid_omnibus = s_config.get_key( "jid" )

            s_log.write( "process start" )
            prc1 = multiprocessing.Process( target = _sapi_runner_omnibus._entrypoint , daemon = True )
            prc1.start( )
            prc_starttime = s_util.uptime( )
            while prc1.is_alive( ) :
                
                ##########
                job_rping = s_net.job_rping( jid_omnibus )
                if(job_rping!=False):
                    if("state" in job_rping and job_rping["state"]=="cancel"):
                        s_log.write( "cancel job!!!!" )
                        prc1.kill( )
                        break

                    #s_log.write(job_rping)
                ##########

                s_util.sleep( 3 )
                # FIXME TODO should be configurable and use actual time not some counter
                if ( s_util.uptime( ) - prc_starttime ) > 900 :
                    s_log.write( "prc_counter!!! KILL" )
                    prc1.kill( )

            prc1.join( )
            # -9 when kill, 1 when exception/error..? 0 is OK
            runner_exitcode = prc1.exitcode
            s_log.write( "process end" )

            ########################################################

            #if( runner_exitcode != 0 ) :
            #    s_log.write( "ERROR _sapi_runner_omnibus runner_exitcode " + str( runner_exitcode ) , consoleprint = True )
            #    continue
        except Exception as e :
            #ERROR _sapi_runner_omnibus Exception module 'sapiadapter.sapiadapter' has no attribute 'write'

            s_log.write( "ERROR _sapi_runner_omnibus Exception " + str( e ) , consoleprint = True )
            s_util.printexception( e )
            s_util.sleep( 3 )
            continue

        #runner_exitcode = _sapi_runner_omnibus._entrypoint( )
        s_log.write( "runner_exitcode " + str( runner_exitcode ) , consoleprint = True )

        #####################################################

        #if runner_exitcode==0:
        s_net.job_set( )

        #####################################################

        s_log.write( "OK" )

#####################################################################################################
runner_internal_ctime = 0
# Required to make module name scope available in function for importlib
_sapi_runner_internal = None
def sapirunner_internal_reloadifchanged( path_runner ) :
    global runner_internal_ctime
    try :
        if( s_util.file_changed( path_runner , runner_internal_ctime ) ) :
            runner_internal_ctime = s_util.file_ctime( path_runner )
            importlib.reload( _sapi_runner_internal )
            s_log.write( "path_runner RELOAD" , consoleprint = True )
            s_util.sleep( 3 )

    except Exception as e :
        s_log.write( "ERROR sapirunner_internal_reloadifchanged " + str( e ) , consoleprint = True )
        s_util.sleep( 3 )
        return( False )

    return( True )


def runner_internal( path_runner ) :

    # Required to make module name scope available in function for importlib
    global _sapi_runner_internal

    s_log.write( "RUNNER_internal START " + path_runner )

    if( not s_util.sys_path_append_fp( path_runner ) ) :
        s_log.write( "ERROR NOT FOUND " + path_runner , consoleprint = True )
        prexit( "ERR" )

    import _sapi_runner_internal

    global runner_internal_ctime
    runner_internal_ctime = s_util.file_ctime( path_runner )

    while True :

        s_util.sleep( 0.1 )

        heartbeat( )

        #####################################################
        if( not sapirunner_internal_reloadifchanged( path_runner ) ) : continue
        #####################################################

        try :
            runner_exitcode = _sapi_runner_internal._entrypoint( )
            if( runner_exitcode > 0 ) :
                s_log.write( "ERROR _sapi_runner_internal runner_exitcode " + str( runner_exitcode ) , consoleprint = True )
                continue
        except Exception as e :
            s_log.write( "ERROR _sapi_runner_internal Exception " + str( e ) , consoleprint = True )
            s_util.sleep( 3 )
            continue

        #####################################################

def omnibus_ping( ) :
    run( {
        "_tests_omnibus_ping" : "y"
    } )
    return( s_db.meta_read( "_job_state" ) == "done" ) 

#####################################################################

# DATA
# TIMEOUT
def run( params = { } , wait_timeout = 60 ) :

    #if( not ready( ) ) :
    #    s_log.write( "NOT READY" )
    #    return( False )


    tid = s_util.thread_get_id()




    if( not isinstance( params , ( dict ) ) ) :
        s_log.write( "false params dict" )
        return( False )

    #####################################################################

    #s_db.flush( ) 

    #####################################################################

    #s_db.meta_create( "_params" , params )

    #####################################################################

    if not s_net.job_request( params ) :
        s_log.write( "false job_request" )
        return( False )

    #####################################################################

    jid = s_config.get_key( "jid" )

    if( jid == False ) :
        s_log.write( "false job_request jid" )
        return( False )

    #####################################################################

    #s_log.write( s_db.meta_read( "_test_run_withresponse" ))
    jr = s_net.job_responsewait( jid , wait_timeout )
    #s_log.write( s_db.meta_read( "_test_run_withresponse" ))

    if( jr == False ) :
        s_log.write( "false job_wait" )
        return( False )

    if( jr == None ) :
        s_log.write( "none job_wait" )
        return( None )

    #####################################################################

    if( s_db.stdio_has_stderr( ) ) :
        s_log.write( "ERROR stdio_has_stderr " + s_db.stdio_get_stderr( ) )
        return( None )

    #####################################################################

    #if( s_db.meta_read( "_runner_exitflag" ) == False ) :
    #    return( False )

    dd = defdata( )
    if( dd == False ) : return( True )
    return( dd )
