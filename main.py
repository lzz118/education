from __future__ import with_statement
import urllib
import webapp2
import csv
import logging
import json

from Crypto.PublicKey import RSA
from Crypto import Random
from StringIO import StringIO
from models import File

from google.appengine.api import files
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import login_required

class MainHandler(webapp2.RequestHandler):
    def get(self):
        landing_page = """
        <html><body>
          <a href="/static/index.html">AJAX Test GUI</a><br>
          <a href="/api/file">all files</a>
        <body/><html/>
        """
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
        
        blob_key = files.blobstore.get_blob_key(file_name)
        self.response.out.write('<html><body>File has uploaded, please download the file at <a href="/serve/%s">here</a>' % blob_key )
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
            encryption_key = RSA.importKey('''-----BEGIN RSA PRIVATE KEY-----
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
        
        enc_data = encryption_key.encrypt(plaintext, 32)
        # encode the byte data into ASCII data so that it could be printed out in the browser
        return enc_data[0].encode('base64')

    @staticmethod
    def save_file(data, encryption_key, has_header_row, delimiter, **kwds):
        logging.info("delimiter is %d [%s]" % (len(delimiter), delimiter))
        columns_for_encryption=kwds['columns_for_encryption']
        columns_info=kwds['columns_info']
        file_name = files.blobstore.create(mime_type='text/plain')

        with files.open(file_name, 'a') as f:
            writer = csv.writer(f , delimiter=delimiter.encode("utf-8"))
            reader = csv.reader(StringIO(data), delimiter=delimiter.encode("utf-8")) 
            
            if has_header_row:
                header_row = next(reader)
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
        file_data = self.request.POST.get('newFile').value
        file_name = self.request.POST.get('newFile').filename
        columns_to_encrypt = self.request.POST.get('columns_to_encrypt', '')
        encrypted_column_indexs = [ int(index)-1 for index in columns_to_encrypt.split(',') if index.isdigit() and int(index) > 0 ]
        description = self.request.POST.get('description', '')
        has_header_row = True if self.request.POST.get('hasHeaderRow', 'No') == 'Yes' else False 
        delimiter = self.request.POST.get('delimiter', ',')
        
        logging.info("Uploaded file_name:[%s] description:[%s] has_header_row:[%s] delimiter:[%s] encrypted_idxs[%s]" % (file_name, description, has_header_row, delimiter, encrypted_column_indexs))

        columns_info = []
        blob_key = FileUtils.save_file(file_data, None, has_header_row, delimiter, columns_for_encryption=encrypted_column_indexs, columns_info=columns_info)
        
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
                               ('/api/file', FileManager),
                               ('/api/file/([^/]+)?', FileManager)],
                              debug=True)
