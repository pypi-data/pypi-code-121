import tornado.ioloop
import tornado.web

def Serving(port, handlers):
    for h in handlers:
        print(h[0])
    application = tornado.web.Application(handlers)
    application.listen(port)
    tornado.ioloop.IOLoop.current().start()