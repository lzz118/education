from google.appengine.ext import db
from google.appengine.api import users

class File(db.Model): 
  name = db.StringProperty()
  description = db.StringProperty()
  content_type = db.StringProperty()
  encryption_meta = db.TextProperty() # A string of encoded json data used to keep track of the columns encrypted by public key.   
  # The link to the file contents in the blobstore. 
  #owner = db.User() #- the person uploading the file.
  created = db.DateTimeProperty(auto_now_add=True)

class PublicKey(db.Model):
  name = db.StringProperty()
  description = db.StringProperty()
  publickey = db.TextProperty() # public encryption key
  #owner - the person uploading the file.
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
