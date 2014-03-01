'''

Implements unit tests for the utility classes

'''

import main
import unittest
from google.appengine.api import users
from api.utils import KeyUtils, FileUtils 
from api.delivery.models import PublicKey
from api.exceptions import InvalidOperation
from unittests.utils import TestCaseWithFiles 

class Test_Utils(TestCaseWithFiles):
    
    def test_save_publickey(self):
        key_data = "DEFAULT_PUBLIC_KEY"
        email = 'tester@gmail.com' 
        key_name = "test encryption key"
        key_description = "This is a test encryption key"
        user = users.User(email)
        is_default_key = False 
        
        is_success = KeyUtils.save_publickey(key_data, key_name, key_description, is_default_key, user)                
        self.assertTrue(is_success)
        
        keys = PublicKey.all().filter('owner = ', user).fetch(1000)
        self.assertEqual(len(keys), 1)
        self.assertEqual(keys[0].publickey, key_data)
        self.assertEqual(keys[0].name, key_name)
        self.assertEqual(keys[0].is_default_key, is_default_key)
        self.assertEqual(keys[0].description, key_description)
    
    def test_get_publickey(self):
        admin_key_data = "DEFAULT_PUBLIC_KEY"
        admin_key_name = "default encryption key"
        admin_key_description = "This is a default encryption key"
        
        user_key_data = "USER_PUBLIC_KEY"
        user_key_name = "user encryption key"
        user_key_description = "This is a user encryption key"
        
        email = 'tester@gmail.com' 
        user = users.User(email)
        admin_email = 'admin@gmail.com' 
        administrator = users.User(admin_email)
       
        # Test Case 1 : Raise an exception if no key is found.
        with self.assertRaises(InvalidOperation):
            KeyUtils.get_publickey(user)

        # Save a default key owned by administrator
        publickey = PublicKey(name=admin_key_name, 
                              description=admin_key_description,
                              publickey=admin_key_data,
                              is_default_key=True,
                              owner=administrator)
        publickey.put()
        self.assertEqual(len(PublicKey.all().fetch(2)), 1)
        
        # Test Case 2 : return default encryption key for a user who has not 
        #               yet uploaded a key.
        key_info_dict, key_data_buffer = KeyUtils.get_publickey(user)
        self.assertEqual(key_data_buffer, admin_key_data)
        self.assertEqual(key_info_dict['key_name'], admin_key_name)
        self.assertEqual(key_info_dict['key_description'], admin_key_description)
        self.assertEqual(key_info_dict['key_owner'], admin_email)
       
        # Save a encryption for the user
        publickey = PublicKey(name=user_key_name, 
                              description=user_key_description,
                              publickey=user_key_data,
                              is_default_key=False,
                              owner=user)
        publickey.put()
        
        # Test Case 3 : fetch encryption key for a user who has uploaded a key.
        key_info_dict, key_data_buffer = KeyUtils.get_publickey(user)
        self.assertEqual(key_data_buffer, user_key_data)
        self.assertEqual(key_info_dict['key_name'], user_key_name)
        self.assertEqual(key_info_dict['key_description'], user_key_description)
        self.assertEqual(key_info_dict['key_owner'], email)
    
    def test_save_csv_file(self):
        #TODO
        pass

    def test_crypt(self):
        #TODO
        pass

    def test_delete_file(self):
        #TODO
        pass

    def test_append_file(self):
        #TODO
        pass
