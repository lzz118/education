'''
Created on Dec 1, 2013

@author: Chris
'''

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import testbed
from google.appengine.ext import blobstore

from django.utils import simplejson as json
from time import sleep
from webtest import TestApp
import webapp2
import unittest
import logging
import main

class Test_Quest(unittest.TestCase):

    def setUp(self):
        
        self.testbed = testbed.Testbed()
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
        self.assertEqual(1,1)
        # Build a request object passing the URI path to be tested.
        # You can also pass headers, query arguments etc.
        request = webapp2.Request.blank('/')
        # Get a response for that request.
        response = request.get_response(main.app)

        # Let's check if the response is correct.
        self.assertEqual(response.status_int, 200)
        self.assertEqual(True, "<form action=" in response.body)
    
    def test_file_upload(self):
        app = TestApp(main.app)
        file_content="1, user1, developer\n2, user2, developer2"  
        response = app.post('/upload', upload_files=[
            ('file', 'test_file.csv', file_content,),
            ])
        
        # Check the content is valid
        self.assertEqual(response.status_int, 200)
        self.assertEqual(True, "File has uploaded" in response.body)
        
        links = response.html.find_all("a")
        self.assertEqual(1, len(links))
        
        # Check if the link is valid
        blobs = blobstore.BlobInfo.all().fetch(limit=2)
        self.assertEqual(1, len(blobs))
        self.assertEqual(links[0]['href'], "/serve/%s" % str(blobs[0].key()))

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
          
