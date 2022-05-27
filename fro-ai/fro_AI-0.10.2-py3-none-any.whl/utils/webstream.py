import cv2
from flask import Response
from flask import Flask
from flask import render_template
import threading
from werkzeug.serving import make_server

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful for multiple browsers/tabs
# are viewing tthe stream)
outputFrame = None
lock = threading.Lock()

# initialize a flask object
app = Flask(__name__)


class ServerThread(threading.Thread):
    def __init__(self, app, port=5000):
        threading.Thread.__init__(self)
        self.srv = make_server('0.0.0.0', port, app, threaded=True)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.server_close()
        self.srv.shutdown()


class WebStreamServer():
    __first_init = True

    def __init__(self, port=5000) -> None:
        if not self.__class__.__first_init:
            return
        self.server = ServerThread(app, port)
        self.server.start()
        self.__class__.__first_init = False

    def render(self, bgr):
        global outputFrame, lock
        with lock:
            outputFrame = bgr.copy()

    def stop(self):
        self.server.shutdown()

    def start(self):
        self.server.start()


@app.route("/")
def index():
    # return the rendered template
    return render_template("index.html")


def generate():
    # grab global references to the output frame and lock variables
    global outputFrame, lock

    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrame is None:
                continue

            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

            # ensure the frame was successfully encoded
            if not flag:
                continue

        # yield the output frame in the byte format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) +
               b'\r\n')


@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")
