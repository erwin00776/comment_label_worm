__author__ = 'erwin'

import BaseHTTPServer

from comment_label_worm.RedisMiddle import *

redis_saver = RedisMiddle()

class RedisCountHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    server_version = "SimpleHTTP/0.6.1"

    def do_GET(self):
        """Serve a GET request."""
        print("Get: " + self.path)

        question_mark = self.path.index("?")
        if question_mark > 0:
            prefix = self.path[:question_mark]
            suffix = self.path[question_mark+1:]
            kv = {}
            for pair in suffix.split("&"):
                p = pair.split("=")
                kv[p[0]] = p[1]
            self.dispatch(prefix, kv)

        self.send_response(200)
        self.send_header("Content-type", 'text/html; charset=utf-8')
        self.send_header("Content-Length", 0)
        self.send_header("Last-Modified", self.date_time_string(time.time()))
        self.end_headers()

    def do_HEAD(self):
        """Serve a HEAD request."""
        pass

    def dispatch(self, prefix, kv={}):
        if prefix == '/rating':
            self.rating(kv)

    def rating(self, kv={}):
        if not ('mid' in kv and 'action' in kv):
            print("bad url: kv=" + kv)
        redis_saver.rating_put(kv['mid'], kv['action'])


def startOnCallServer(port=8000):
    #HandlerClass = SimpleHTTPRequestHandler

    HandlerClass = RedisCountHandler

    ServerClass = BaseHTTPServer.HTTPServer
    Protocal = "HTTP/1.0"

    server_address = ('127.0.0.1', port)
    HandlerClass.protocol_version = Protocal
    httpd = ServerClass(server_address=server_address, RequestHandlerClass=HandlerClass)

    sa = httpd.socket.getsockname()
    print("start oncall server on: %s:%d" % (sa[0], sa[1]))
    httpd.serve_forever()

if __name__=='__main__':

    startOnCallServer(8000)