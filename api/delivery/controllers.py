"""

"""

import urllib
import webapp2
import logging
import json

from google.appengine.api import users
from webapp2_extras.appengine.users import login_required

from api.utils import FileUtils
from api.delivery.models import File


class FileApiHandler(webapp2.RequestHandler):
   
    def delete(self, key):
        if key:
            FileUtils.delete_file(key)
        else:
            self.abort(400)
    
    @login_required
    def get(self, parameter=None):
        if parameter:
            decoded_parameter = str(urllib.unquote(parameter))
            if decoded_parameter.endswith("csv"):
                # Serves /api/file/<key>.csv : GET
                # returns the file content if there is a match
                blob_key = decoded_parameter.split(".")[0]
                blob_info =FileUtils.get_blob_info(blob_key)
                if blob_info:
                    self.send_blob(blob_info)
                else:
                    self.abort(404)
            else:
                self.abort(400)
        else:
            # Serves /api/file : GET
            # returns 50 most file descriptions of the current logged in user, sorted by last modification date.
            user = users.get_current_user()
            self.response.write('<html><body>Hello %s! [<a href=%s>sign out</a>]' % \
                (user.nickname(), users.create_logout_url(self.request.uri)
                ))
            self.response.write("<h1>File List</h1><ol>")
            files = File.all().order("-last_modified").filter('owner =', user).fetch(50)
            for file in files:
                self.response.write('''
                <li> <a href='/serve/%s'>Open file</a></li> 
                name:[%s] <br/> 
                description:[%s] <br/>
                has_header_row:[%s] <br/>
                delimiter:[%s] <br/>
                encryption_meta[%s]<br/>
                last_modified[%s]<br/><br/> 
                ''' % (file.file_key, file.name, file.description, file.has_header_row, file.delimiter, file.encryption_meta, file.last_modified) )  
            self.response.write("</ol></body></html>")

    def post(self):
        # Serves /api/file : POST 
        if not len(self.request.get('newFile')):
            self.abort(400)
        
        user = users.get_current_user()
        if not user:
            self.abort(400)
        
        file_data = self.request.POST.get('newFile').value
        file_name = self.request.POST.get('newFile').filename
        columns_to_encrypt = self.request.POST.get('columns_to_encrypt', '')
        encrypted_column_indexs = [ int(index)-1 for index in columns_to_encrypt.split(',') if index.isdigit() and int(index) > 0 ]
        description = self.request.POST.get('description', '')
        has_header_row = True if self.request.POST.get('hasHeaderRow', 'No') == 'Yes' else False 
        delimiter = self.request.POST.get('delimiter', ',')
        
        logging.info("Uploaded file_name:[%s] description:[%s] has_header_row:[%s] delimiter:[%s] encrypted_idxs[%s]" % (file_name, description, has_header_row, delimiter, encrypted_column_indexs))

        columns_info = []
        [ encryption_key_info, encryption_key ] = FileUtils.get_publickey(user)
        blob_key = FileUtils.save_csv_file(file_data, encryption_key, has_header_row, delimiter, columns_for_encryption=encrypted_column_indexs, columns_info=columns_info)
        
        new_file = File()
        new_file.name = file_name
        new_file.description = description 
        new_file.has_header_row = has_header_row 
        new_file.file_key = str(blob_key)
        new_file.delimiter = delimiter
        new_file.encryption_meta = {"encryption_key_info": encryption_key_info, "columns_info": columns_info }
        new_file.owner = user 
        new_file.put()

        response = {'name': file_name, 'key': str(blob_key), 'lastUpdate': str(new_file.last_modified)}        
        self.response.write(json.dumps(response))
