"""Education WSGI app 

"""
import os

import webapp2


debug = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')
app = webapp2.WSGIApplication(
    [
        webapp2.Route(
            r'/',
            handler='education.controllers.MainHandler',
            name='home'
        ),
        webapp2.Route(
            r'/upload',
            handler='education.controllers.UploadHandler',
            name='upload'
        ),
        webapp2.Route(
            r'/serve/([^/]+)?',
            handler='education.controllers.ServeHandler',
            name='serve'
        ),
        webapp2.Route(
            r'/admin',
            handler='education.admin.controllers.AdminConsoleHandler',
            name="admin.console"
        ),
        webapp2.Route(
            r'/admin/([^/]+)?',
            handler='education.admin.controllers.AdminConsoleHandler',
            name="admin.console.action"
        ),
        webapp2.Route(
            r'/api/admin',
            handler='education.admin.controllers.AdminApiHandler'
        ),
        webapp2.Route(
            r'/api/admin/([^/]+)?',
            handler='education.admin.controllers.AdminApiHandler'
        ),
        webapp2.Route(
            r'/api/file',
            handler='education.api.controllers.FileApiHandler'
        ),
        webapp2.Route(
            r'/api/file/([^/]+)?',
            handler='education.api.controllers.FileApiHandler'
        ),
    ],
    debug=debug
)
