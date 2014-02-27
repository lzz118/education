"""Education WSGI app

"""
import os

import webapp2
from webapp2_extras import routes


debug = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')

# TODO: move existing api route here
apiv1_route = routes.PathPrefixRoute(
    r'/api/v1',
    [
        webapp2.Route('/user.json', 'api.controllers.UserApi'),
        webapp2.Route('/students.json', 'api.controllers.StudentApi'),
    ]
)

app = webapp2.WSGIApplication(
    [
        webapp2.Route(r'/', 'api.controllers.MainHandler', name='home'),
        webapp2.Route(
            r'/upload', 'api.controllers.UploadHandler', name='upload'
        ),
        webapp2.Route(
            r'/serve/([^/]+)?', 'api.controllers.ServeHandler', name='serve'
        ),
        webapp2.Route(
            r'/admin',
            'api.admin.controllers.AdminConsoleHandler',
            name="admin.console"
        ),
        webapp2.Route(
            r'/admin/([^/]+)?',
            'api.admin.controllers.AdminConsoleHandler',
            name="admin.console.action"
        ),
        webapp2.Route(r'/api/admin', 'api.admin.controllers.AdminApiHandler'),
        webapp2.Route(
            r'/api/admin/([^/]+)?', 'api.admin.controllers.AdminApiHandler'
        ),
        webapp2.Route(r'/api/file', 'api.api.controllers.FileApiHandler'),
        webapp2.Route(
            r'/api/file/([^/]+)?', 'api.api.controllers.FileApiHandler'
        ),
        apiv1_route
    ],
    debug=debug
)
