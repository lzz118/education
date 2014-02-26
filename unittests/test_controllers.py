"""Test controllers for common task

"""
import webapp2
from webtest import TestApp
from google.appengine.ext import ndb

import main
from unittests.utils import TestCase
from api.models import Student


class TestStudentApi(TestCase):
    """Test for StudentApi request handler.

    """
    def setUp(self):
        super(TestStudentApi, self).setUp()

        self.request = webapp2.Request.blank('')
        self.request.META = {}
        self.request.META['REMOTE_ADDR'] = '1.2.3.4'
        self.app = TestApp(main.app)
        self.alice = Student.new_student({
            'firstName': 'Alice',
            'lastName': 'Smith',
            'matricule': 'X2010200001'
        })
        # make sure data will be visible in next query
        ndb.get_multi(
            [
                self.alice.key
            ],
            use_cache=False
        )

    def tearDown(self):
        self.testbed.deactivate()

    def testStudentList(self):
        """Should list students

        TODO: Handle authentication and authorisation
        It probably should only be allowed for staff.

        """
        response = self.app.get('/api/v1/students.json')
        self.assertEqual(response.status_int, 200)
        self.assertIn('cursor', response.json)
        self.assertIn('students', response.json)
        self.assertEqual(
            response.json.get('students'),
            [
                {
                    'firstName': 'Alice',
                    'lastName': 'Smith',
                    'matricule': 'X2010200001',
                }
            ]
        )

    def testStudentListWithCursor(self):
        """Should list students using the cursor for a previous request

        """
        response = self.app.get('/api/v1/students.json')
        self.assertEqual(response.status_int, 200)

        # might be empty in production
        self.assertTrue(response.json.get('cursor'))
        response = self.app.get(
            '/api/v1/students.json', {'cursor': response.json.get('cursor')}
        )
        self.assertIn('cursor', response.json)
        self.assertIn('students', response.json)
        self.assertEqual(response.json.get('students'), [])
