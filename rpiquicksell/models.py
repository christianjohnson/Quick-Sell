from google.appengine.ext import db

class Book(db.Model):
  """Models an individual book."""
  isbn = db.IntegerProperty()
  title = db.StringProperty()
  user = db.UserProperty()
  description = db.StringProperty(multiline=True)
  price = db.FloatProperty()
  date = db.DateTimeProperty(auto_now_add=True)