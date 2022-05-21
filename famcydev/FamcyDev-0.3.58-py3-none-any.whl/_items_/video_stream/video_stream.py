import json
import Famcy
from flask import current_app
import urllib
import time
from threading import Thread
import cv2
import base64

class video_stream(Famcy.FamcyBlock):
    """
    Represents the block to display
    video_stream. 
    """
    def __init__(self, **kwargs):
        self.uniq_channal = "video"+str(id(self))
        self.del_thread()
        self.value = video_stream.generate_template_content()

        super(video_stream, self).__init__(**kwargs)

        self.init_block()
        self.is_alive = False
        self.end_thread = False


    def del_thread(self):
        if self.get_cookie("uniq_channal") and Famcy.FManager[self.get_cookie("uniq_channal")]:
            Famcy.FManager[self.get_cookie("uniq_channal")] = False
        self.set_cookie("uniq_channal", self.uniq_channal)

    @classmethod
    def generate_template_content(cls, fblock_type=None):
        """
        This is the function that
        returns the template content 
        for the given fblock. 
        - Return a content dictionary
        """
        return {
            "video_link": 'rtsp://rtsp.stream/pattern',
            "stream_flag": True,
            "delay": 1,
            "route_name": "/",
            "snap": False,
            "size": None,   # [100,60]
        }

    def init_block(self):
        self.body = Famcy.div()
        self.body["id"] = self.id

        _s = Famcy.script()
        _s.innerHTML = _event_source_script = '''
            var source = new EventSource("/event_source?channel=event_source.%s");
            source.addEventListener('publish', function(event) {
                var data = JSON.parse(event.data);
                update_event_source_target(data)
            }, false);
            source.addEventListener('error', function(event) {
                console.log("Error"+ event)
            }, false);
            ''' % (self.uniq_channal)

        self.body.addStaticScript(_s)

    def send_frame(self):
        with Famcy.app.app_context():
            capture = cv2.VideoCapture(self.value["video_link"])
            while self.value["stream_flag"] and self.is_alive and Famcy.FManager[self.uniq_channal]:
                time.sleep(self.value["delay"])
                frame = capture.read()[1]
                if self.value["size"]:
                    frame = cv2.resize(frame, (self.value["size"][0], self.value["size"][1])) 
                cnt = cv2.imencode('.jpg',frame)[1]
                b64 = base64.b64encode(cnt).decode("utf-8")
                html = "<img src='data:image/jpeg;base64,"+str(b64) +"'>"
                Famcy.sse.publish({"indicator": True, "message": {"target_id": self.id, "target_innerHTML": html, "target_attribute": {}}}, type='publish', channel='event_source.'+self.uniq_channal)
            
            # set end thread flag True when the thread is dead
            self.end_thread = True

    def send_a_frame(self):
        capture = cv2.VideoCapture(self.value["video_link"])
        frame = capture.read()[1]
        if self.value["size"]:
            frame = cv2.resize(frame, (self.value["size"][0], self.value["size"][1])) 
        cnt = cv2.imencode('.jpg',frame)[1]
        b64 = base64.b64encode(cnt).decode("utf-8")
        return "data:image/jpeg;base64,"+str(b64)

    def render_inner(self):
        if not self.value["snap"]:
            # create new threads
            if not self.is_alive:
                self.is_alive = True
                t1 = Thread(target=self.send_frame, daemon=True)
                t1.start()

            else:
                self.is_alive = False
                while not self.end_thread:
                    pass
                self.end_thread = False
                self.is_alive = True
                t1 = Thread(target=self.send_frame, daemon=True)
                t1.start()

            Famcy.FManager[self.uniq_channal] = self.is_alive
                
        else:
            self.body.children = []
            _i = Famcy.img()
            _i["src"] = self.send_a_frame()
            self.body.addElement(_i)

        return self.body