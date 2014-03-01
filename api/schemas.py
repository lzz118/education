"""Resolve json schema

TODO: share them with the GUI apps
"""

from jsonschema import Draft4Validator, RefResolver


_base_uri = 'http://nextucloud.appspot.com'

_education_schemas = {
    "id": "%s/schemas/education.json#" % _base_uri,
    "$schema": "http://json-schema.org/draft-04/schema#",
    "student": {
        "id": "#student",
        "title": "Student schema",
        "type": "object",
        "properties": {
            "lastName": {"type": "string"},
            "firstName": {"type": "string"},
            "matricule": {"type:": "string"},
        },
        "required": ["firstName", "lastName", "matricule"]
    },
    "user": {
        "id": "#user",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "logoutUrl": {"type:": "string"},
        },
        "required": ["name"]
    },
    "loginError": {
        "id": "#login-error",
        "type": "object",
        "properties": {
            "loginUrl": {"type:": "string"},
            "error": {"type:": "string"},
        },
        "required": ["error", "loginUrl"]
    }
}

_portfolio_schemas = {
    "id": "%s/schemas/education/portfolio.json#" % _base_uri,
    "$schema": "http://json-schema.org/draft-04/schema#",
    "portfolio": {
        "id": "#portfolio",
        "title": "Student schema for portfolio",
        "type": "object",
        "properties": {
            "student":{
                "$ref": "%s/schemas/education.json#student" % _base_uri,
            },
            "exams": {
                "type": "object",
                "patternProperties": {
                    "^[-\w\d]+$": {
                        "$ref": "#/exam"
                    }
                },
                "additionalProperties": False,
            },
            "evaluations": {
                "type": "object",
                "patternProperties": {
                    "^[-\w\d]+$": {
                        "$ref": "#/evaluation"
                    }
                },
                "additionalProperties": False,
            },
        },
        "required": ["student", "exams", "evaluations"]
    },

    "exam": {
        "id": "#exam",
        "title": "Student exam result schema",
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "student": {"$ref": "%s/schemas/education.json#student" % _base_uri},
            "groupName": {"type": "string"},
            "data": {
                "type": "array",
                "items": {
                    "$ref": "#/examData"
                }
            }
        },
         "required": ["id", "name", "student", "groupName", "data"]
    },
    "examData": {
        "id": "#exam-data",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "min": {"$ref": '#/examResult'},
            "max": {"$ref": '#/examResult'},
            "student": {"$ref": '#/examResult'},
        },
        "required": ["name", "min", "max", "student"]
    },
    "examResult": {
        "id": "#exam-result",
        "type": "number",
        "minimum": -2,
        "maximum": 2,
    },

    "evaluation": {
        "id": "#evaluation",
        "title": "Student evaluation result schema",
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "student": {
                "$ref": "%s/schemas/education.json#student % _base_uri"
            },
            "groupName": {"type": "string"},
            "data": {
                "type": "array",
                "items": {
                    "$ref": "#/evaluationData"
                }
            }
        },
        "required": ["id", "name", "student", "groupName", "data"]
    },
    "evaluationData": {
        "id": "#evaluation-data",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "mean": {"$ref": '#/evaluationResult'},
            "student": {"$ref": '#/evaluationResult'},
        },
        "required": ["name", "mean", "student"]
    },
    "evaluationResult": {
        "id": "#evaluation-result",
        "type": "number",
        "minimum": -1,
        "maximum": 1,
    },
}

resolver = RefResolver(
    _base_uri,
    {},
    store={
        '%s/schemas/education.json' % _base_uri: _education_schemas,
        '%s/schemas/education/portfolio.json' % _base_uri: _portfolio_schemas,
    }
)

with resolver.resolving('schemas/education.json#student') as schema:
    student = Draft4Validator(schema, resolver=resolver)

with resolver.resolving('schemas/education/portfolio.json#portfolio') as schema:
    portfolio = Draft4Validator(schema, resolver=resolver)
