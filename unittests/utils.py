"""Utility class and function for education test cases.

"""


import unittest
import main
import webapp2

from google.appengine.api import users
from google.appengine.ext import testbed
from google.appengine.api.blobstore import blobstore_stub, file_blob_storage
from google.appengine.api.files import file_service_stub
from google.appengine.datastore import datastore_stub_util
from google.appengine.ext import blobstore
from webtest import TestApp, AppError
from api.delivery.models import PublicKey


class TestCase(unittest.TestCase):
    """Basic Test case to extends

    Setup google appengine mock services.

    """

    def setUp(self):
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.

        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(
            probability=0
        )
        self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)
        self.testbed.init_memcache_stub()
        self.testbed.init_mail_stub()
        self.testbed.init_blobstore_stub()
        self.testbed.init_files_stub()
        self.testbed.init_taskqueue_stub(root_path="../.") #2.7
        self.testbed.init_user_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def login(self, is_admin=False):
        # Simulate User login
        self.testbed.setup_env(
            USER_EMAIL = 'test@example.com',
            USER_ID = '123',
            USER_IS_ADMIN = '1' if is_admin else '0',
            overwrite = True)
    
    def create_testkey(self):
        key_data = "DEFAULT_PUBLIC_KEY"
        email = 'tester@gmail.com' 
        key_name = "test encryption key"
        key_description = "This is a test encryption key"
        user = users.User(email)
        testkey = PublicKey(name=key_name, 
                            description=key_description,
                            publickey=key_data,
                            is_default_key=False,
                            owner=user)
        testkey.put()
        return testkey.key().id()

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

class TestCaseWithFiles(TestCase):
    def setUp(self):
        self.testbed = TestbedWithFiles()
        self.testbed.activate()
        
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_mail_stub()
        self.testbed.init_blobstore_stub()
        self.testbed.init_taskqueue_stub(root_path="../.") #2.7
        self.testbed.init_user_stub()
        
        self.request = webapp2.Request.blank('')
        self.request.META = {}
        self.request.META['REMOTE_ADDR'] = '1.2.3.4'
        self.app = TestApp(main.app)
