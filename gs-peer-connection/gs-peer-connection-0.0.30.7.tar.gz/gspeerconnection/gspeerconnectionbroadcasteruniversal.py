import ast
import json
import logging
import platform
import socketio
from aiortc import RTCPeerConnection, RTCRtpSender, RTCConfiguration, RTCIceServer, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRelay


pcs = set()

def create_local_tracks(play_from, decode, device, rtbufsize):
    global relay, webcam

    if play_from:
        player = MediaPlayer(play_from, decode=decode)
        return player.audio, player.video
    else:
        options = {"framerate": "30", "video_size": "640x480", "rtbufsize": rtbufsize}
        if relay is None:
            if platform.system() == "Darwin":
                webcam = MediaPlayer(
                    "default:none", format="avfoundation", options=options
                )
            elif platform.system() == "Windows":
                webcam = MediaPlayer(
                    f"video={device}", format="dshow", options=options
                )
            else:
                webcam = MediaPlayer(f"{device}", format="v4l2", options=options)
            relay = MediaRelay()
        return None, relay.subscribe(webcam.video)


def force_codec(pc, sender, forced_codec):
    kind = forced_codec.split("/")[0]
    codecs = RTCRtpSender.getCapabilities(kind).codecs
    transceiver = next(t for t in pc.getTransceivers() if t.sender == sender)
    transceiver.setCodecPreferences(
        [codec for codec in codecs if codec.mimeType == forced_codec]
    )


class GSPeerConnectionBroadcasterUniversal:

    @classmethod
    async def create(cls, gsdbs):
        self = GSPeerConnectionBroadcasterUniversal()
        self.rtconfiList = []
        self.gsdbs = gsdbs
        if self.gsdbs.credentials["stunenable"]:
            self.rtconfiList.append(RTCIceServer(self.gsdbs.credentials["stunserver"]))
        if self.gsdbs.credentials["turnenable"]:
            self.rtconfiList.append(RTCIceServer(urls=self.gsdbs.credentials["turnserver"],
                                                 username=self.gsdbs.credentials["turnuser"],
                                                 credential=self.gsdbs.credentials["turnpw"]
                                                 ))

        self.sio = socketio.AsyncClient()
        self.peerConnections = {}
        self._logger = logging.getLogger(__name__)
        self.webcam = None
        self.relay = None

        @self.sio.event
        async def connect():
            self._logger.info('connection established')

        @self.sio.event
        async def watcher(id, description):
            if type(description) == str:
                description = ast.literal_eval(description)
            desc = type('new_dict', (object,), description)

            offer = RTCSessionDescription(sdp=description["sdp"], type=description["type"])

            if len(self.rtconfiList) > 0:
                pc = RTCPeerConnection(configuration=RTCConfiguration(self.rtconfiList))
            else:
                pc = RTCPeerConnection()

            pcs.add(pc)

            @pc.on("connectionstatechange")
            async def on_connectionstatechange():
                print("Connection state is %s" % pc.connectionState)
                if pc.connectionState == "failed":
                    await pc.close()
                    pcs.discard(pc)

            audio, video = create_local_tracks(False,
                                               decode=not True,
                                               device=self.gsdbs.credentials["webcam"],
                                               rtbufsize=self.gsdbs.credentials["rtbufsize"])

            if video:
                video_sender = pc.addTrack(video)
                force_codec(pc, video_sender, "video/H264")

            await pc.setRemoteDescription(offer)

            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)

            await self.sio.emit("answer", {"id": id,
                                           "message": json.dumps(
                                               {"type": pc.localDescription.type,
                                                "sdp": pc.localDescription.sdp})})

        @self.sio.event
        async def joined():
            await self.sio.emit("broadcaster")

        @self.sio.event
        async def disconnectPeer(id):
            if id in self.peerConnections:
                await self.peerConnections[id].close()
                self.peerConnections.pop(id, None)

        @self.sio.event
        async def disconnect():
            self._logger.info('disconnected from server')

        connectURL = ""

        if "localhost" in self.gsdbs.credentials["signalserver"]:
            connectURL = f'{self.gsdbs.credentials["signalserver"]}:{str(self.gsdbs.credentials["signalport"])}'
        else:
            connectURL = self.gsdbs.credentials["signalserver"]

        await self.sio.connect(
            f'{connectURL}?gssession={self.gsdbs.cookiejar.get("session")}.{self.gsdbs.cookiejar.get("signature")}{self.gsdbs.credentials["cnode"]}')
        await self.sio.wait()
