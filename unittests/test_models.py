'''
Created on Jan 8, 2014

@author: Chris
'''
from api.delivery import models
from unittests.utils import TestCase


class Test_Models(TestCase):

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
