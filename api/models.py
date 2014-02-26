"""Common models for all api branches

"""

import jsonschema
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor


# TODO: save in portfolio GUI project instead
STUDENT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "Student Schema",
    "type": "object",
    "properties": {
        "lastName": {"type": "string"},
        "firstName": {"type": "string"},
        "matricule": {"type:": "string"},
    },
    "required": ["firstName", "lastName", "matricule"]
}


class Student(ndb.Model):
    """Student entity model.

    Note:

    - most of a the student data with be stored in the data attribute.
    - Retrieving or setting  part of the data with be done via
    properties
    - indexing part of the data will be done with
    ndb.ComputedProperty attribute.

    TODO: handle authentication, taking into account that a student
    entity might not be create by a student.

    """
    data = ndb.JsonProperty()

    @property
    def matricule(self):
        return self.key.id()

    @property
    def last_name(self):
        return self.data.get('lastName')

    @property
    def first_name(self):
        return self.data.get('firstName')

    @property
    def photo(self):
        return self.data.get('photo')

    @classmethod
    @ndb.transactional(xg=True, retries=0)
    def new_student(cls, data):
        """Create a new student entity from its json representation

        """
        existing_student = Student.get_by_id(data['matricule'])
        if existing_student:
            raise AttributeError(
                "A student with a same matricule already exists."
            )

        student = cls(id=data['matricule'], data=data)
        student.put()
        return student

    def _pre_put_hook(self):
        """Make sure data attribute is validate format some field
        before saving an entity.

        Note: idealy, formatting would not happen at this stage, but it
        simplify queries since queries over text is case sensitive.

        """
        self.validate(self.data)
        if self.key and self.key.id() != self.data['matricule']:
            raise AttributeError("The student matricule cannot be edited")

        for prop_name in ["firstName", "lastName"]:
            self.data[prop_name] = self.data[prop_name].title()

    @classmethod
    def get_students(cls, cursor_key=None):
        """Get the list of student, 20 at a time.

        return a list of student, a cursor for the next query and boolean
        indication if there might be more student to query.

        """
        cursor = Cursor(urlsafe=cursor_key) if cursor_key else None
        return cls.query().fetch_page(20, start_cursor=cursor)

    @staticmethod
    def validate(data):
        """Validate student data schema.

        """
        jsonschema.validate(data, STUDENT_SCHEMA)
