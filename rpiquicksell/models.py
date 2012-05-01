from google.appengine.ext import db

class UniqueBook(db.Model):
  isbn = db.StringProperty(required=True)
  title = db.StringProperty(required=True)
  lastAdded = db.DateTimeProperty()
  sellpage = db.StringProperty(required=True)
  requery = db.BooleanProperty()

class Book(db.Model):
  """Models an individual book."""
  unique = db.ReferenceProperty(UniqueBook,collection_name="books")
  isbn = db.StringProperty()
  description = db.StringProperty()
  user = db.UserProperty()
  condition = db.StringProperty()
  price = db.FloatProperty()
  is_local = db.BooleanProperty()
  url = db.StringProperty()
  external_store = db.StringProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  sold_date = db.DateTimeProperty()

"""class User(db.Model):
  username = db.UserProperty(required=True)"""
