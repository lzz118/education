"""Utility class and function for education test cases.

"""


import unittest

from google.appengine.ext import testbed


class TestCase(unittest.TestCase):
    """Basic Test case to extends

    Setup google appengine mock services.

    """

    def setUp(self):
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_mail_stub()
        self.testbed.init_blobstore_stub()
        self.testbed.init_files_stub()
        self.testbed.init_taskqueue_stub(root_path="../.") #2.7
        self.testbed.init_user_stub()
        
    def tearDown(self):
        self.testbed.deactivate()
