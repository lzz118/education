from google.appengine.ext import db
from google.appengine.api import users
import json
import logging

# http://kovshenin.com/2010/app-engine-json-objects-google-datastore/
class JsonProperty(db.TextProperty):
    def validate(self, value):
        return value
    
    def get_value_for_datastore(self, model_instance):
        result = super(JsonProperty, self).get_value_for_datastore(model_instance)
        result = json.dumps(result)
        return db.Text(result)

    def make_value_from_datastore(self, value):
        try:
            value = json.loads(str(value))
        except:
            pass
        return super(JsonProperty, self).make_value_from_datastore(value)

class File(db.Model): 
  name = db.StringProperty()
  description = db.StringProperty()
  has_header_row = db.BooleanProperty()
  file_key = db.StringProperty()
  last_modified = db.DateTimeProperty(auto_now_add=True)
  delimiter = db.StringProperty()
  description = db.StringProperty()
  content_type = db.StringProperty()
  encryption_meta = JsonProperty() # A string of encoded json data used to keep track of the columns encrypted by public key.   
  # The link to the file contents in the blobstore. 
  owner = db.UserProperty() # the person uploading the file.

class PublicKey(db.Model):
  name = db.StringProperty()
  description = db.StringProperty()
  publickey = db.TextProperty() # public encryption key
  owner = db.UserProperty() #- the person uploading the file.
  created = db.DateTimeProperty(auto_now_add=True)
  
class ScheduledUpload(db.Model): 
  name = db.StringProperty()
  description = db.StringProperty()
  #start_date
  #end_date
  #frequency #String - yearly, monthly, weekly, daily
  #owner - the person uploading the file.
  created = db.DateTimeProperty(auto_now_add=True)

class ScheduledUploadFileAssociation(db.Model): 
  #schedule
  file = db.ReferenceProperty(File, required=True)
  created = db.DateTimeProperty(auto_now_add=True)
