from google.appengine.ext import db

class Book(db.Model):
  """Models an individual book."""
  isbn = db.IntegerProperty()
  title = db.StringProperty()
  user = db.UserProperty()
  condition = db.StringProperty()
  price = db.FloatProperty()
  is_local = db.BooleanProperty()
  date = db.DateTimeProperty(auto_now_add=True)
