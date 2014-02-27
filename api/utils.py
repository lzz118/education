import json
import csv
import logging
from StringIO import StringIO

import webapp2
from Crypto.PublicKey import RSA
from google.appengine.api import files
from google.appengine.ext import blobstore
from google.appengine.ext import db


class JsonProperty(db.TextProperty):
    """Json model property

    extends TextProperty to pack and unpack json content.

    see: http://kovshenin.com/2010/app-engine-json-objects-google-datastore/

    """
    def validate(self, value):
        return value

    def get_value_for_datastore(self, model_instance):
        result = super(JsonProperty, self).get_value_for_datastore(
            model_instance
        )
        result = json.dumps(result)
        return db.Text(result)

    def make_value_from_datastore(self, value):
        try:
            value = json.loads(str(value))
        except Exception:
            pass
        return super(JsonProperty, self).make_value_from_datastore(value)


class FileUtils:

    @staticmethod
    def crypt(plaintext, encryption_key):
        if not encryption_key:
            return plaintext
        enc_data = RSA.importKey(encryption_key).encrypt(plaintext, 32)
        # encode the byte data into ASCII data so that it could be printed
        # out in the browser
        return enc_data[0].encode('base64')

    @staticmethod
    def get_publickey(user):
        keys=[]
        if user:
            # Get the keyfor the user
            keys.extend(PublicKey.all().filter('owner = ', user).run(batch_size=1000))
        # Get the default key, we shall only have one
        keys.extend(PublicKey.all().filter('is_default_key = ', True).fetch(1))
        if len(keys) == 0:
            logging.error("No encryption key found for user %s" % user.nickname())
            self.abort(400)
        logging.info("Return encryption key with name [%s] , description [%s] , owned by [%s] for user %s" %
                     (keys[0].name, keys[0].description, keys[0].owner.nickname(), user.nickname()))
        return ({'key_name' : (keys[0]).name, 'key_description' : (keys[0]).description, 'key_owner' : (keys[0]).owner.email() }, (keys[0]).publickey)

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
        if blob_key:
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


class ApiRequestHandler(webapp2.RequestHandler):
    """Base Request Handler for json API Request

    """

    def render_json(self, data, status_code=200):
        self.response.status = status_code
        self.response.headers['Content-Type'] = "application/json"
        self.response.write(json.dumps(data))
