'''
Created on Jan 8, 2014

@author: Chris
'''

import unittest

from google.appengine.ext import testbed
from google.appengine.api.blobstore import blobstore_stub, file_blob_storage
from google.appengine.api.files import file_service_stub

from education.delivery import models


class TestbedWithFiles(testbed.Testbed):
    """See http://stackoverflow.com/questions/8130063/test-function-with-google-app-engine-files-api"""

    def init_blobstore_stub(self):
        blob_storage = file_blob_storage.FileBlobStorage(
            '/tmp/testbed.blobstore',
            testbed.DEFAULT_APP_ID
        )
        blob_stub = blobstore_stub.BlobstoreServiceStub(blob_storage)
        file_stub = file_service_stub.FileServiceStub(blob_storage)
        self._register_stub('blobstore', blob_stub)
        self._register_stub('file', file_stub)


class Test_Models(unittest.TestCase):

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
        
    def tearDown(self):
        self.testbed.deactivate()

    def test_file(self):
        f = models.File()
        f.put()
        self.assertEqual(1,models.File.all().count())

    def test_publickey(self):
        pk = models.PublicKey()
        pk.put()
        self.assertEqual(1,models.PublicKey.all().count())

    def test_ScheduledUpload(self):
        su = models.ScheduledUpload()
        su.put()
        self.assertEqual(1,models.ScheduledUpload.all().count())

    def test_ScheduledUploadFileAssociation(self):
        f = models.File()
        f.put()
        
        sua = models.ScheduledUploadFileAssociation(file=f)
        sua.put()
        self.assertEqual(1,models.ScheduledUploadFileAssociation.all().count())
