import logging
import json
import urllib
import webapp2
from google.appengine.api import users
from webapp2_extras.appengine.users import admin_required

from api.utils import FileUtils, KeyUtils
from api.delivery.models import PublicKey


class AdminConsoleHandler(webapp2.RequestHandler):
    """
        Handler for the Admin console test page.
    """
    def _admin_console(self):
        key_list = "<table border='1'><th>ID</th><th>Key Name</th><th>Key Description</th><th>Owner</th><th>Created</th><th>Default Key</th><th>Action</th>"
        publickeys = PublicKey.all().run(batch_size=1000)
        for seq, publickey in enumerate(publickeys):
            key_list += "<tr><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td><a href='/admin/edit_key?id=%s'>edit</a><br/><a href='/api/admin/delete_key?id=%s'>delete</a></td></tr>" % \
                        (seq+1, publickey.name, publickey.description, publickey.owner,
                        str(publickey.created), publickey.is_default_key, publickey.key().id(), publickey.key().id())
        key_list += "</table>"
        admin_landing_page = """
        <html><title> Admin Console Test Page</title><body>
            <h1> Upload a new default encryption key </h1>
            <form action="/api/admin" enctype="multipart/form-data" method="post">
                Please upload a key: <input type="file" name="default_public_key"><br>
                <input type="submit">
            </form>
            <br>
            <h1> Upload a new encryption key for user</h1>
            <form action="/api/admin" enctype="multipart/form-data" method="post">
                User email: <input type="text" name="email"><br>
                Please upload a key: <input type="file" name="default_public_key"><br>
            <input type="submit">
            </form>
            <br>
            <h1> Key List </h1>
            <ol>%s</ol>
            <br>
        </body></html>
        """ % key_list
        self.response.out.write(admin_landing_page)
    
    def _edit_key(self, key_data, key_id):
        edit_encryption_key_form = """
                                   <html>
                                        <body>
                                            <form action='/api/admin/edit_key'>
                                                <textarea rows='10' cols='50' name='key_data'>%s</textarea>
                                                <input type="hidden" name='id' value='%s'/>
                                                <input type="submit" value='save change'/>
                                            </form>
                                        </body>
                                   </html>
                                   """ % (key_data, key_id)
        self.response.out.write(edit_encryption_key_form)

    @admin_required
    def get(self, action=None):
        if not action:
            return self._admin_console()
        elif action == 'edit_key':
            id = self.request.get('id', None)
            if id:
                public_key = PublicKey.get_by_id(long(id))
                if public_key:
                    return self._edit_key(public_key.publickey, id)
                return self.abort(404)
            return self.abort(400)


class AdminApiHandler(webapp2.RequestHandler):
    
    @admin_required
    def get(self, id=None):
        """
            Serve /api/admin GET method for testing the admin apis.
        """
        response = []
        publickeys = []
        if id:
            # For testing
            #if action == "delete_key":
            #    self.delete()
            # For testing
            #elif action == "edit_key":
            #    self.put()
            #else
            id = str(urllib.unquote(id))
            publickeys = [PublicKey.get_by_id(long(id))]
        else:
            publickeys = PublicKey.all().run(batch_size=1000)
        
        for seq, publickey in enumerate(publickeys):
            response.append({ 'key_name'  : publickey.name, 'key_description' : publickey.description, 
                                'key_owner' : str(publickey.owner.email()), 'created' : str(publickey.created), 
                                'is_default_key' : publickey.is_default_key, 'key_id' : publickey.key().id()})
        self.response.out.write(json.dumps(response))

    def post(self):
        """
            Serve /api/admin POST method. It supports the uploading of encryption keys.
        """
        user = users.get_current_user()
        if not user or not users.is_current_user_admin():
            self.abort(400)
        key_data = self.request.POST.get('default_public_key').value
        email = self.request.POST.get('email', '')
        key_name = "default encryption key"
        key_description = "This is the default encryption key used when no user encryption key found."
        is_default_key = True
        if len(email) > 0:
            is_default_key = False
            user = users.User(email)
            key_name = "encryption key for %s" % user.nickname()
            key_description = "The encryption key used for encrypting data uploaded by %s" % user.nickname()
        is_success = KeyUtils.save_publickey(key_data, key_name, key_description, is_default_key, user)                
        self.response.write({'status' : 'success' if is_success else 'failure'})
    
    def delete(self, id=None):
        """
            Serves /api/admin/id DELETE method.  It supports the deletion of the encryption keys by key id.
        """
        if id:
            id = str(urllib.unquote(id))
            public_key = PublicKey.get_by_id(long(id))
            if public_key:
                public_key.delete()
                self.response.write({'status' : 'success'})
                return
            else:
                self.abort(404)
        self.abort(400)

    def put(self, id=None):
        """
            Serves /api/admini/id PUT method. It supports the changing of the encryption key value by key id.
        """
        key_data = self.request.get('key_data', None)
        if id and key_data:
            id = str(urllib.unquote(id))
            public_key = PublicKey.get_by_id(long(id))
            if public_key:
                public_key.publickey = key_data
                public_key.put()
                self.response.write({'status' : 'success'})
                return
            else:
                self.abort(404)
        self.abort(400)
