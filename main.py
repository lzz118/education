"""Education WSGI app 

"""
import os

import webapp2


debug = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')
app = webapp2.WSGIApplication(
    [
        webapp2.Route(
            r'/',
            handler='api.controllers.MainHandler',
            name='home'
        ),
        webapp2.Route(
            r'/upload',
            handler='api.controllers.UploadHandler',
            name='upload'
        ),
        webapp2.Route(
            r'/serve/([^/]+)?',
            handler='api.controllers.ServeHandler',
            name='serve'
        ),
        webapp2.Route(
            r'/admin',
            handler='api.admin.controllers.AdminConsoleHandler',
            name="admin.console"
        ),
        webapp2.Route(
            r'/admin/([^/]+)?',
            handler='api.admin.controllers.AdminConsoleHandler',
            name="admin.console.action"
        ),
        webapp2.Route(
            r'/api/admin',
            handler='api.admin.controllers.AdminApiHandler'
        ),
        webapp2.Route(
            r'/api/admin/([^/]+)?',
            handler='api.admin.controllers.AdminApiHandler'
        ),
        webapp2.Route(
            r'/api/file',
            handler='api.api.controllers.FileApiHandler'
        ),
        webapp2.Route(
            r'/api/file/([^/]+)?',
            handler='api.api.controllers.FileApiHandler'
        ),
    ],
    debug=debug
)
