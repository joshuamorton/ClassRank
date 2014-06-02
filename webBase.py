"""
a
"""

import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("hello world")

class IndexHandler(tornado.web.RequestHandler):
    def get(self, id):
        self.write(id)



applicationee = tornado.web.Application([
    (r"/index/(\d+)/", IndexHandler),
    (r"/", MainHandler),
])



if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()