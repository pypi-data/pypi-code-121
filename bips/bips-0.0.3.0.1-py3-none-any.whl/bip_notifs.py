from pysinewave import SineWave
import time

def base_beep( frequency, duration, pause = 0.3 ):
    sinewave = SineWave( pitch = frequency )
    sinewave.play( )
    time.sleep( duration )
    sinewave.stop( )

    time.sleep( pause )


def error_beep( ):
    for i in range( 0, 7 ):
        base_beep( 30.2, 0.15 )


def done_status_beep( ):
    for i in range( 0, 2 ):
        base_beep( 7.5, 0.15 )

    time.sleep( 0.1 )

    for i in range( 0, 2 ):
        base_beep( 19.4, 0.15 )


def success_beep( ):
    for i in range( 0, 1 ):
        base_beep( 19.4, 1 )

    time.sleep( 0.1 )

    for i in range( 0, 2 ):
        base_beep( 19.4, 0.15 )
