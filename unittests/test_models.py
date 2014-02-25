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
        self.assertTrue(models.File.get(f.key()))

    def test_publickey(self):
        pk = models.PublicKey()
        pk.put()
        self.assertTrue(models.PublicKey.get(pk.key()))

    def test_ScheduledUpload(self):
        su = models.ScheduledUpload()
        su.put()
        self.assertTrue(models.ScheduledUpload.get(su.key()))

    def test_ScheduledUploadFileAssociation(self):
        f = models.File()
        f.put()
        
        sua = models.ScheduledUploadFileAssociation(file=f)
        sua.put()
        self.assertTrue(models.ScheduledUploadFileAssociation.get(sua.key()))
