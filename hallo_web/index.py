__author__ = 'erwin'

import web

urls = (
    '/world(/.*)', 'World',
    '/(.*)', 'Hallo',
)

app = web.application(urls, globals())


class Hallo:
    def GET(self, name):
        if not name:
            name = 'Hallo'
        return 'hello, ' + name

class World:
    def GET(self, name):
        if not name:
            name = 'World'
        return 'world, ' + name


if __name__ == '__main__':
    app.run()