from __future__ import with_statement
import urllib
import webapp2
import csv
import logging
from StringIO import StringIO

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import files
from Crypto.PublicKey import RSA
from Crypto import Random

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
        
        #blob_key = files.blobstore.get_blob_key(file_name)
        #self.response.out.write('<html><body>File has uploaded, please download the file at <a href="/serve/%s">here</a>' % blob_key )
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
    def crypt(plaintext):
        return plantext

    @staticmethod
    def save_file(data):
        file_name = files.blobstore.create(mime_type='text/plain')
        with files.open(file_name, 'a') as f:
            writer = csv.writer(f , delimiter=',')
            for row in csv.reader(StringIO(data), delimiter=','):
                if len(row) > 1:
                    row[1] = self.crypt(row[1])
                writer.writerow(row)
        files.finalize(file_name)
        blob_key = files.blobstore.get_blob_key(file_name)
        logging.get_logger("Utils").debug("A new file has been uploaded and saved with key %s" % blog_key)

    @staticmethod
    def delete_file(key=None):
        if key:
            pass
        else:
            # Delete all files
            pass

    @staticmethod
    def append_file(key, data):
        pass

    @staticmethod
    def fetch_file(key):
        pass
    
    @staticmethod
    def replace_file(key, newfile):
        pass

    @staticmethod
    def update_meta_data(key, meta_info):
        pass

    @staticmethod
    def get_meta_data(user, limit):
        pass

class FileManager(blobstore_handlers.BlobstoreDownloadHandler):

    def get(self, key=None):
        FileUtils.fetch_file(key)
        pass

    def post(self, key=None):
        file_name = self.request.POST.get('name', 'filename')
        has_header_row = self.request.POST.get('hasHeaderRow', True)
        delimiter = self.request.POST.get('delimiter', ',')
        file = self.request.POST.get('newFile').value

app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/upload', UploadHandler),
                               ('/serve/([^/]+)?', ServeHandler),
                               ('/api/file', FileManager),
                               ('/api/file/([^/]+)?', FileManager)],
                              debug=True)
