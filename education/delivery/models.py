"""Models for content delivery api

"""

from google.appengine.ext import db

from education.utils import JsonProperty


class File(db.Model):
    """Model for file entity.

    """
    name = db.StringProperty()
    description = db.StringProperty()
    has_header_row = db.BooleanProperty()
    file_key = db.StringProperty()
    last_modified = db.DateTimeProperty(auto_now_add=True)
    delimiter = db.StringProperty()
    description = db.StringProperty()
    content_type = db.StringProperty()
    # A string of encoded json data used to keep track of the columns
    # encrypted by public key.
    encryption_meta = JsonProperty()
    # The link to the file contents in the blobstore.
    # the person uploading the file.
    owner = db.UserProperty()


class PublicKey(db.Model):
    """Model for a public key entity.

    """
    name = db.StringProperty()
    description = db.StringProperty()
    publickey = db.TextProperty() # public encryption key
    owner = db.UserProperty() #- the person uploading the file.
    created = db.DateTimeProperty(auto_now_add=True)


class ScheduledUpload(db.Model):
    """Model for a schedule upload entity.

    """
    name = db.StringProperty()
    description = db.StringProperty()
    #start_date
    #end_date
    #frequency #String - yearly, monthly, weekly, daily
    #owner - the person uploading the file.
    created = db.DateTimeProperty(auto_now_add=True)


class ScheduledUploadFileAssociation(db.Model):
    """Model associating file and a shedule upload (?)

    """
    #schedule
    file = db.ReferenceProperty(File, required=True)
    created = db.DateTimeProperty(auto_now_add=True)
