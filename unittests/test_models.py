'''
Created on Jan 8, 2014

@author: Chris
'''
from api.delivery import models
from api.models import Student
from unittests.utils import TestCase
from jsonschema import ValidationError

class TestModels(TestCase):

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


class TestStudent(TestCase):

    def test_new_student(self):
        alice = Student.new_student({
            'firstName': 'Alice',
            'lastName': 'Smith',
            'matricule': 'X2010200001'
        })
        self.assertEqual('X2010200001', alice.matricule)
        self.assertEqual('X2010200001', alice.key.id())
        self.assertEqual('Alice', alice.first_name)
        self.assertEqual('Smith', alice.last_name)
        self.assertEqual(None, alice.photo)

        alice = Student.get_by_id('X2010200001')
        self.assertTrue(alice)

    def test_new_student_create_unique_student(self):
        Student.new_student({
            'firstName': 'Alice',
            'lastName': 'Smith',
            'matricule': 'X2010200001'
        })
        self.assertRaises(
            AttributeError,
            Student.new_student,
            {
                'firstName': 'Bob',
                'lastName': 'Smith',
                'matricule': 'X2010200001' # same matricule
            }
        )

        alice = Student.get_by_id('X2010200001')
        self.assertEqual('Alice', alice.first_name)

    def test_validate_student(self):
        self.assertEqual(
            None,
            Student.validate(
                {
                    'firstName': 'Alice',
                    'lastName': 'Smith',
                    'matricule': 'X2010200001',
                    'photo': 'http://placehold.it/300x400&text=portrait'
                }
            )
        )
        self.assertRaises(
            ValidationError,
            Student.validate,
            {
                'matricule': 'X2010200001'
            }
        )
        self.assertRaises(
            ValidationError,
            Student.validate,
            {
                'firstName': 'Alice',
                'lastName': 'Smith',
            }
        )

    def test_update_student(self):
        """the student data stay valide"""
        Student.new_student({
            'firstName': 'Alice',
            'lastName': 'Smith',
            'matricule': 'X2010200001'
        })
        alice = Student.get_by_id('X2010200001')
        del alice.data['lastName']
        self.assertRaises(ValidationError, alice.put)

    def test_matricule_is_immutable(self):
        """The student matricule cannot be edited"""
        Student.new_student({
            'firstName': 'Alice',
            'lastName': 'Smith',
            'matricule': 'X2010200001'
        })
        alice = Student.get_by_id('X2010200001')
        alice.data['matricule'] += '1'
        self.assertRaises(AttributeError, alice.put)

    def test_names_are_capitalized(self):
        alice = Student.new_student({
            'firstName': 'alice',
            'lastName': 'smith',
            'matricule': 'X2010200001'
        })
        self.assertEqual('Alice', alice.first_name)
        self.assertEqual('Smith', alice.last_name)

        alice = Student.get_by_id('X2010200001')
        alice.data['lastName'] = 'taylor'
        alice.put()
        self.assertEqual('Taylor', alice.last_name)
