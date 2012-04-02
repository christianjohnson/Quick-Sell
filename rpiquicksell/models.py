from google.appengine.ext import db

class Book(db.Model):
  """Models an individual book."""
  isbn = db.StringProperty()
  title = db.StringProperty()
  user = db.UserProperty()
  condition = db.StringProperty()
  price = db.FloatProperty()
  is_local = db.BooleanProperty()
  url = db.StringProperty()
  external_store = db.StringProperty()
  date = db.DateTimeProperty(auto_now_add=True)

class UniqueBook(db.Model):
  isbn = db.StringProperty(required=True)
  title = db.StringProperty(required=True)
  lastAdded = db.DateTimeProperty()
  sellpage = db.StringProperty(required=True)
