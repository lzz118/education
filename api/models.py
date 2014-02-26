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
        "fullName": {"type:": "string"}
    },
    "required": ["firstName", "lastName", "matricule"]
}


class Student(ndb.Model):
    """Student entity model.

    """
    data = ndb.JsonProperty(validator=lambda p, v: Student.validate(v))

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
    def new_student(cls, data):
        """Create a new student entity from its json representation

        """
        @ndb.transactional(xg=True, retries=0)
        def tx():
            existing_student = Student.get_by_id(data['matricule'])
            if existing_student:
                raise AttributeError(
                    "A student with a same matricule already exists."
                )

            student = cls(id=data['matricule'], data=data)
            student.put()
            return student
        return tx()

    @classmethod
    def get_students(cls, cursor_key=None):
        cursor = Cursor(urlsafe=cursor_key) if cursor_key else None
        return cls.query().fetch_page(20, start_cursor=cursor)

    @staticmethod
    def validate(data):
        """Validate student data

        """
        jsonschema.validate(data, STUDENT_SCHEMA)
