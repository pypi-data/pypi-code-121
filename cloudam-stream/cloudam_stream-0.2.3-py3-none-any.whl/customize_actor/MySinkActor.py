from loguru import logger

from cloudam_stream.core.actors import SinkActor

from cloudam_stream.core.ports.inputports import TextInputPort


class MySinkActor(SinkActor):
    title = "My sink actor"
    name = "Sink"
    intake = TextInputPort()

    def begin(self):
        self.file = open("result.txt", "w+")
        print("------start sink actor")
        self.i = 0

    def write(self, item, port):
        print("------running sink actor")
        try:
            self.file.write(item)
        except:
            logger.info("error:")
        if self.i % 1000:
            self.file.flush()
        self.i += 1

    def end(self):
        print("------stop sink actor")
        self.file.close()
