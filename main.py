import os
import tornado.ioloop
import tornado
import tornado.web
import tornado.websocket

from snek import Snek


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class SnekHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('snek.html', username=self.get_argument("username", None))


class SnekWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        id = self.get_argument("id", None)
        username = self.get_argument("username", None)
        snek.add_player(self, id, username)

    def on_message(self, message):
        snek.receive_message(message)

    def on_close(self):
        snek.remove_player(self)


# Create game
snek = Snek()

# Create settings dict
settings = dict(
    template_path=os.path.join(os.path.dirname(__file__), 'templates'),
    static_path=os.path.join(os.path.dirname(__file__), 'static'),
    debug=True
)

# Create server
application = tornado.web.Application([
    (r"/", MainHandler), (r"/snek", SnekHandler), (r"/snekSocket/", SnekWebSocket)
], **settings)

# Start server
if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()
