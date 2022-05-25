# NOT WORKING
import ctypes as ct
import ctypes.util

lib = ct.CDLL(ctypes.util.find_library("3DconnexionClient"))

# Callbacks
# (connection)
ConnexionAddedHandlerProc = ct.CFUNCTYPE(None, ct.c_uint)
# (connection)
ConnexionRemovedHandlerProc = ct.CFUNCTYPE(None, ct.c_uint)
# (connection, messageType, *messageArgument)
ConnexionMessageHandlerProc = ct.CFUNCTYPE(None, ct.c_uint, ct.c_uint, ct.c_void_p)

SetConnexionHandlers = lib.SetConnexionHandlers
SetConnexionHandlers.restype = ct.c_int16
SetConnexionHandlers.argtypes = [
    ConnexionMessageHandlerProc,
    ConnexionAddedHandlerProc,
    ConnexionRemovedHandlerProc,
    ct.c_bool,  # useSeparateThread
]
RegisterConnexionClient = lib.RegisterConnexionClient
RegisterConnexionClient.restype = ct.c_uint16
RegisterConnexionClient.argtypes = [
    ct.c_uint32,  # signature
    ct.POINTER(ct.c_uint8),  # *name
    ct.c_uint16,  # mode
    ct.c_uint32,  # mask
]


@ConnexionMessageHandlerProc
def handle_msg(connection: int, messageType: int, messageArgument) -> None:
    print("handle_msg", locals())


@ConnexionAddedHandlerProc
def handle_added(connection):
    print("handle_added", locals())


@ConnexionRemovedHandlerProc
def handle_removed(connection):
    print("handle_removed", locals())


kConnexionClientWildcard = 0x2A2A2A2A
kConnexionClientModeTakeOver = 1
kConnexionClientModePlugin = 2
kConnexionMaskAll = 0x3FFF
ITRM = 0x4954524D


def register():
    err = SetConnexionHandlers(handle_msg, handle_added, handle_removed, True)
    assert not err
    print("connected")

    clientID = RegisterConnexionClient(
        kConnexionClientWildcard, None, kConnexionClientModeTakeOver, kConnexionMaskAll
    )
    print("client", clientID)
