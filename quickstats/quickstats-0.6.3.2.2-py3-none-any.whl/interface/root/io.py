import ROOT

def redirect_print_stream(streamer):
    old_streamer = ROOT.RooPrintable.defaultPrintStream(streamer)
    return old_streamer

def get_default_stream():
    return ROOT.RooPrintable.defaultPrintStream()