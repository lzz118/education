'''
Created on Dec 1, 2013

@author: Chris
'''
import csv

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import testbed
from google.appengine.api.blobstore import blobstore_stub, file_blob_storage
from google.appengine.api.files import file_service_stub

from google.appengine.ext import blobstore

from django.utils import simplejson as json
from time import sleep
from webtest import TestApp
from Crypto.PublicKey import RSA

import webapp2
import unittest
import logging
import main

PRIVATE_KEY = '''-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----'''
PUBLIC_KEY = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCIJAdEmiawxYaf/ZTv/679mwxi
wJPhHsKPIfoW8w0IRy0oZhkSzp+M+UGIiKL3FDJjMkVVl8mpxJ8qMwkTkRte8+1G
oxPRANmuvEsAIVpfVctJkIqJ+FTcH8J28hPugIJFrWD4tWcPslr75s8fx0VJjcOk
dV5gZAea2JlXKaXEvQIDAQAB
-----END PUBLIC KEY-----'''

class TestbedWithFiles(testbed.Testbed):
    """See http://stackoverflow.com/questions/8130063/test-function-with-google-app-engine-files-api"""

    def init_blobstore_stub(self):
        blob_storage = file_blob_storage.FileBlobStorage('/tmp/testbed.blobstore',
                                                testbed.DEFAULT_APP_ID)
        blob_stub = blobstore_stub.BlobstoreServiceStub(blob_storage)
        file_stub = file_service_stub.FileServiceStub(blob_storage)
        self._register_stub('blobstore', blob_stub)
        self._register_stub('file', file_stub)

class Test_CSV_Row_Encryption(unittest.TestCase):

    def setUp(self):
        self.testbed = TestbedWithFiles()
        
        #self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_mail_stub()
        self.testbed.init_blobstore_stub()
        self.testbed.init_taskqueue_stub(root_path="../.") #2.7
        
        self.request = webapp2.Request.blank('')
        self.request.META = {}
        self.request.META['REMOTE_ADDR'] = '1.2.3.4'

    def tearDown(self):
        self.testbed.deactivate()

    def test_index(self):
        app = TestApp(main.app)
        response = app.get('/')
        # User needs to login before redirected to the home page.
        self.assertEqual(response.status_int, 302)
    
    def test_crypt(self):
        key = RSA.importKey(PRIVATE_KEY)
        for username in ['chris', 'bob', 'mary-joe add']:
            enc_data = main.UploadHandler.crypt(username)
            decrypted = key.decrypt(enc_data.decode('base64'))
            self.assertEqual(username, decrypted)

    def test_file_upload(self):
        app = TestApp(main.app)
        file_content="1, user1, developer\n2, user2, developer2"  
        response = app.post('/upload', upload_files=[
            ('file', 'test_file.csv', file_content,),
            ])
        
        # Check the content is valid
        self.assertEqual(response.status_int, 200)
        self.assertEqual(True, "File 1" in response.body)
        
        links = response.html.find_all("a")
        self.assertEqual(1, len(links))
        
        # Check if the link is valid
        blobs = blobstore.BlobInfo.all().fetch(limit=2)
        self.assertEqual(1, len(blobs))
        self.assertEqual(links[0]['href'], "/serve/%s" % str(blobs[0].key()))

    def test_upload_ecryption_decryption(self):
        csv_file = 'a,1234\nb,4567'
        app = TestApp(main.app)
        response = app.post('/upload', upload_files=[
                ('key', 'id_rsa.pub', PUBLIC_KEY,),
                ('file', 'file.csv', csv_file,),
            ])
        self.assertEqual(response.status_int, 200)
        self.assertEqual(True, "File 1" in response.body)

        blobs = blobstore.BlobInfo.all().fetch(limit=2)
        self.assertEqual(1, len(blobs))

        enc_csv = blobstore.BlobReader(blobs[0].key())
        rows = {}
        key = RSA.importKey(PRIVATE_KEY)
        for row in csv.reader(enc_csv, delimiter=','):
            print row
            self.assertEqual(2, len(row))
            rows[row[0]] = key.decrypt(row[1].decode('base64'))

        self.assertEqual(2, len(rows))
        self.assertEqual('1234', rows['a'])
        self.assertEqual('4567', rows['b'])
    
    def test_pycrypto(self):
        from Crypto.PublicKey import RSA
        from Crypto import Random
        random_generator = Random.new().read
        key = RSA.generate(1024, random_generator)

        self.assertEqual(True, key.can_encrypt())
        self.assertEqual(True, key.can_sign())
        self.assertEqual(True, key.has_private())

        public_key = key.publickey()
        
        for username in ['chris', 'bob', 'mary-joe add']:
            enc_data = public_key.encrypt(username, 32)
            decrypted = key.decrypt(enc_data)
            self.assertEqual(username, decrypted)
          
