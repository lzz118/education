from __future__ import with_statement
import urllib
import webapp2
import csv
import logging
import json

from Crypto.PublicKey import RSA
from Crypto import Random
from StringIO import StringIO
from models import File, PublicKey
from functools import wraps

from google.appengine.api import files
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from webapp2_extras.appengine.users import login_required, admin_required

class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        header = ""
        if not user:
            header = "You haven't login. Please <a href='%s'>login</a> <br/>" % (users.create_login_url(self.request.uri))
        elif users.is_current_user_admin():
            header = "You have logged in as admin. Go to <a href='/api/admin'>admin page</a>"
        else:
            header = "You have logged in as %s." % user.nickname()

        landing_page = """
        <html><body>
          <h2>%s</h2>
          <a href="/static/index.html">AJAX Test GUI</a><br>
          <a href="/api/file">all files</a>
        <body/><html/>
        """ % header
        self.response.out.write(landing_page)

class UploadHandler(webapp2.RequestHandler):
        
    @staticmethod
    def crypt(plaintext):
        # Use a fixed private key here to get a deterministic result for testing
        key = RSA.importKey('''-----BEGIN RSA PRIVATE KEY-----
        MIICXAIBAAKBgQCIJAdEmiawxYaf/ZTv/679mwxiwJPhHsKPIfoW8w0IRy0oZhkS
        zp+M+UGIiKL3FDJjMkVVl8mpxJ8qMwkTkRte8+1GoxPRANmuvEsAIVpfVctJkIqJ
        +FTcH8J28hPugIJFrWD4tWcPslr75s8fx0VJjcOkdV5gZAea2JlXKaXEvQIDAQAB
        AoGAOkVJgxiD5Pe2xrYQUKVcrhn2NDJ/WUUEO6VsWPRRKLDmaDtDEiS0b++kGB97
        uUvAwWqb+KXOYEbTZYmQofpi/yKSzDIgJy04u2LSmyAvlWrJzj3GE6NbHPv/ctlY
        YUD51TFn3cc97TYCH+fW7HPxpbrRDr9sHvIC7f3vV5HuFJUCQQC6n23oUH3xQeIb
        oNFLQ/GAIQULYQOEYSJv7Vy3nzkkNAKQxDP9/OcYgsGcK3VxzHVrjQVOjFX/kM1L
        d+OtqjtbAkEAusBPWAqUT2CGenG11Vwz5dy1RP4k+xYjI7RLh7dsxGrAshl8YYVx
        ILMvYtNNOFlo9cVCc7zRmUKu175j7kOzxwJBALX8pKwoWjh7W+g/UfnInueoy4eG
        KmzcYD2vxXuWvJ1OTrYnbuAe0Kj5UZ5eTuATVunzkhpABdj7twcCObdvywMCQEHH
        cysjrtG2widm3hFlBLK2ZvMCQaxfQ8lTvDb1mM4me/E/oNwI0Kwf8VTx8IUkmR/Y
        d2uk2n8NSeCcIz7NggkCQFylnC7S7hlgZyUvaIpBsGzzdr8cyrTol4T1G9n7G2sE
        Q1pc7/sXaYlMBZxKrCMWjAol9AZ2Cfpj6x5A3XnTm98=
        -----END RSA PRIVATE KEY-----''')
    
        enc_data = key.encrypt(plaintext, 32)
        
        # encode the byte data into ASCII data so that it could be printed out in the browser
        return enc_data[0].encode('base64')
    
    def post(self):
        rows=self.request.POST.get('file').value
        file_name = files.blobstore.create(mime_type='text/plain')
        with files.open(file_name, 'a') as f:
            writer = csv.writer(f , delimiter=',')
            for row in csv.reader(StringIO(rows), delimiter=','):
                if len(row) > 1:
                    row[1] = self.crypt(row[1])
                writer.writerow(row)
        files.finalize(file_name)
        blobs = blobstore.BlobInfo.all()
        blob_links = [
                      '<a href="/serve/%s">File %s</a><br/>' % (blob.key(), index+1)
                      for index, blob in enumerate(blobs)
                     ]
        
        self.response.out.write(
            '''
               <html>
                 <body>
                 <form action="/upload" enctype="multipart/form-data" method="post"><input type="file" name="file"/><input type="submit" /></form><br>
                 %s
                 </body>
                </html>
            ''' % "".join(blob_links)
        )
class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)

class FileUtils:
    
    @staticmethod
    def crypt(plaintext, encryption_key):
        if not encryption_key:        
            return plaintext 
        enc_data = RSA.importKey(encryption_key).encrypt(plaintext, 32)
        # encode the byte data into ASCII data so that it could be printed out in the browser
        return enc_data[0].encode('base64')
    
    @staticmethod
    def get_publickey(user):
        keys=[]
        if user:
            # Get the keyfor the user
            keys.extend(PublicKey.all().filter('owner = ', user).fetch(10))
        # Get the default key, we shall only have one
        keys.extend(PublicKey.all().filter('is_default_key = ', True).fetch(1))
        if len(keys) == 0:
            logging.error("No encryption key found for user %s" % user.nickname())
            self.abort(400)
        logging.info("Return encryption key with name [%s] , description [%s] , owned by [%s] for user %s" %
                     (keys[0].name, keys[0].description, keys[0].owner.nickname(), user.nickname()))
        return (keys[0]).publickey

    @staticmethod
    def save_publickey(key_data, key_name, key_description, is_default_key, user):
        if is_default_key:
            # Delete old default key, we only keep one at a time
            query = PublicKey.all().filter('is_default_key = ', True)
            for key in query:
                logging.info("Deleting default keys")
                key.delete()

        file_name = files.blobstore.create(mime_type='text/plain')
        with files.open(file_name, 'a') as f:
            f.write(key_data) 
        files.finalize(file_name)
        blob_key = files.blobstore.get_blob_key(file_name)
        publickey = PublicKey(name=key_name, 
                              description=key_description,
                              publickey=key_data,
                              is_default_key=is_default_key,
                              owner=user)
        publickey.put()
        logging.info("Added a new keys with key name [%s] and key description [%s] for %s. It is a %s " % 
                     (key_name, key_description, user.nickname(), "default encryption key" if is_default_key else "user encryption key"))
        return True

    @staticmethod
    def save_csv_file(data, encryption_key, has_header_row, delimiter, **kwds):
        columns_for_encryption=kwds['columns_for_encryption']
        columns_info=kwds['columns_info']
        file_name = files.blobstore.create(mime_type='text/plain')

        with files.open(file_name, 'a') as f:
            writer = csv.writer(f , delimiter=delimiter.encode("utf-8"))
            reader = csv.reader(StringIO(data), delimiter=delimiter.encode("utf-8")) 
            
            if has_header_row:
                header_row = next(reader)
                # If there is a header line, then populate the column names
                for idx, header in enumerate(header_row):
                    columns_info.append({'column_name':header, 'encrypted':True if idx in columns_for_encryption else False})
                writer.writerow(header_row)
            
            longest_row_len = 0
            for row in reader:
                if longest_row_len < len(row):
                    longest_row_len = len(row)
                
                for index in columns_for_encryption:
                    if index < len(row):
                        row[index] = FileUtils.crypt(row[index], encryption_key)
                writer.writerow(row)
            
            # If there is no header line, calculate the size of the longest row, then set the column names to be empty
            if longest_row_len and not columns_info and not has_header_row:
                for idx in range(longest_row_len):
                    columns_info.append({'column_name':'', 'encrypted': True if idx in columns_for_encryption else False})

        files.finalize(file_name)
        blob_key = files.blobstore.get_blob_key(file_name)
        logging.info("A new file has been uploaded and saved with key %s" % blob_key)
        return blob_key

    @staticmethod
    def delete_file(key=None):
        if key:
            blobstore.delete([key])
        else:
            # Delete all files
            pass

    @staticmethod
    def append_file(key, data):
        pass

    @staticmethod
    def get_blob_info(blob_key):
        if key:
            return blobstore.BlobInfo.get(blob_key)
        return None

    @staticmethod
    def replace_file(key, newfile):
        pass

    @staticmethod
    def update_meta_data(key, meta_info):
        pass

    @staticmethod
    def get_meta_data(user, limit):
        pass

class AdminManager(webapp2.RequestHandler):
    
    @admin_required
    def get(self):
        """
            Serve /admin/api GET method for testing the admin apis.
        """
        key_list = ""
        publickeys = PublicKey.all().fetch(100)
        for publickey in publickeys:
            key_list += "<li> key name: %s ,  key description: %s, owner: %s, created: %s, is_default_key: %s" % \
                        (publickey.name, publickey.description, publickey.owner,
                        str(publickey.created), publickey.is_default_key)
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

    def post(self):
        """
            Serve /admin/api POST method. It supports the uploading of encryption keys.
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
        is_success = FileUtils.save_publickey(key_data, key_name, key_description, is_default_key, user)                
        self.response.write({'status' : 'success' if is_success else 'failure'})

class FileManager(webapp2.RequestHandler):
   
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
        encryption_key = FileUtils.get_publickey(user)
        blob_key = FileUtils.save_csv_file(file_data, encryption_key, has_header_row, delimiter, columns_for_encryption=encrypted_column_indexs, columns_info=columns_info)
        
        new_file = File()
        new_file.name = file_name
        new_file.description = description 
        new_file.has_header_row = has_header_row 
        new_file.file_key = str(blob_key)
        new_file.delimiter = delimiter
        new_file.encryption_meta = {"encryption_key": '', "columns_info": columns_info }
        new_file.owner = user 
        new_file.put()

        response = {'name': file_name, 'key': str(blob_key), 'lastUpdate': str(new_file.last_modified)}        
        self.response.write(json.dumps(response))

app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/upload', UploadHandler),
                               ('/serve/([^/]+)?', ServeHandler),
                               ('/api/admin', AdminManager),
                               ('/api/file', FileManager),
                               ('/api/file/([^/]+)?', FileManager)],
                              debug=True)
