'''
Implements the unit tests for testing the /api/admin Rest API
'''
import json
import unittest
from webtest import AppError
from api.admin.controllers import AdminApiHandler 
from unittests.utils import TestCaseWithFiles

class Test_Admin(TestCaseWithFiles):

    def test_api_admin_get(self):
        self.login()
        with self.assertRaises(AppError) as contextmgr: 
            response = self.app.get('/api/admin')
        self.assertTrue("403" in str(contextmgr.exception))
        
        # User must login as admin
        self.login(True)
        
        id = self.create_testkey()
        id2 = self.create_testkey()

        # Test Case 1 : Get the information for a encryption key by key id.
        response = self.app.get('/api/admin/%s' % id)
        self.assertEqual(response.status_int, 200)
        singlekey = json.loads(str(response.body))
        self.assertEqual(len(singlekey), 1)
        self.assertEqual(singlekey[0]['key_id'], id)
        
        # Test Case 2 : Get the information for all encryption key found in the datastore.
        response = self.app.get('/api/admin')
        self.assertEqual(response.status_int, 200)
        allkeys = json.loads(str(response.body))
        self.assertEqual(len(allkeys), 2)

    def test_api_admin_delete(self):
       
        # Test Case 1 : looking for an invalid key id
        with self.assertRaises(AppError) as contextmgr: 
            response = self.app.delete('/api/admin/123')
        self.assertTrue("404" in str(contextmgr.exception))

        # Test Case 2 : delete key by a valid key id, check response
        id = self.create_testkey()
        response = self.app.delete('/api/admin/%d' % id)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body, "{'status': 'success'}")
