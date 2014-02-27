"""Main Html handlers

Demo file upload and encryption.

"""

import urllib
import webapp2
import csv
from StringIO import StringIO

from Crypto.PublicKey import RSA

from google.appengine.api import files
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from webapp2_extras.appengine.users import login_required
from jsonschema import ValidationError

from api.utils import ApiRequestHandler
from api import models


class MainHandler(webapp2.RequestHandler):
    """Handler for the homepage.

    """
    @login_required
    def get(self):
        """Index page.

        """
        user = users.get_current_user()
        header = ""
        if users.is_current_user_admin():
            header = (
                "You have logged in as admin. Go to <a href='/admin'>"
                "admin page</a><br/><a href=%s>logout</a>"
                    % users.create_logout_url(self.request.uri)
            )
        else:
            header = (
                "You have logged in as %s. <a href=%s>logout</a>"
                    % (
                        user.nickname(),
                        users.create_logout_url(self.request.uri),
                    )
            )

        landing_page = """
        <html><body>
          <h2>%s</h2>
          <a href="/static/index.html">AJAX Test GUI</a><br>
          <a href="/api/file">all files</a>
        <body/><html/>
        """ % header
        self.response.out.write(landing_page)


class UploadHandler(webapp2.RequestHandler):
    """File uploader

    """

    @staticmethod
    def crypt(plaintext):
        """Encrypt plain text.

        """
        # Use a fixed private key here to get a deterministic result
        # for testing
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

        # encode the byte data into ASCII data so that it could be printed
        # out in the browser
        return enc_data[0].encode('base64')

    def post(self):
        """Store a file after encripting it.

        """
        rows = self.request.POST.get('file').value
        file_name = files.blobstore.create(mime_type='text/plain')
        with files.open(file_name, 'a') as raw_file:
            writer = csv.writer(raw_file, delimiter=',')
            for row in csv.reader(StringIO(rows), delimiter=','):
                if len(row) > 1:
                    row[1] = self.crypt(row[1])
                writer.writerow(row)
        files.finalize(file_name)
        # TODO: with high replication, the newly created file will not
        # show in the list.
        #
        # It show redirect to a page listing the files instead
        blobs = blobstore.BlobInfo.all()
        blob_links = [
            '<a href="/serve/%s">File %s</a><br/>' % (blob.key(), index+1)
            for index, blob in enumerate(blobs)
        ]

        self.response.out.write("""<html>
    <body>
        <form action="/upload" enctype="multipart/form-data" method="post">
            <input type="file" name="file"/><input type="submit" />
        </form>
        <br>
        %s
    </body>
</html>
            """ % "".join(blob_links)
        )


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    """Serve a file.

    """
    def get(self, resource):
        """Serve file

        """
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)


class StudentApi(ApiRequestHandler):
    """Handle Student resource.

    """

    def get(self):
        """List all students (20 per page)

        """
        cursor_key = self.request.GET.get('cursor')
        students, cursor, _ = models.Student.get_students(cursor_key)
        return self.render_json({
            'students': [s.data for s in students],
            'cursor': cursor.urlsafe() if cursor else ''
        })

    def post(self):
        """Create a new student

        """
        try:
            student = models.Student.new_student(self.request.json)
        except ValidationError, e:
            self.render_json({'error': e.message}, 400)
        else:
            self.render_json(student.data)
