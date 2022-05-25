from enum import Enum
class SOCKET_TYPE(Enum):
    TCPIP=0
    UDP=1

class SOCKET_EVENT(Enum):
    onError="onerror"
    beginRecv="beginrecv"
    onRecv="onrecv"
    onRecvComplete="onrecvcomplete"
    beginSend="beginsend"
    onSend="onsend"
    onSendComplete="onsendcomplete"
    beginListen="beginlisten"
    onListen="onlisten"
    onListenComplete="onlistencomplete"
    beginBind="beginbind"
    onBind="onbind"
    onBindComplete="onbindcomplete"
    beginClose="beginclose"
    onClose="onclose"
    onCloseComplete="onclosecomplete"
    beginConnection="beginconnection"
    onConnection="onconnection"
    onConnectionComplete="onconnectioncomplete"
    beginAccept="beginaccept"
    onAccept="onaccept"
    onAcceptcomplete="onacceptcomplete"