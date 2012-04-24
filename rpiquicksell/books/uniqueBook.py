import models
import datetime
import urllib

class UniqueBook(object):
  
  def __init__(self, isbn, title=''):
    book = models.UniqueBook.all().filter('isbn =',isbn).get()
    if book:
      self.book = book
      self.isbn = book.isbn
      self.title = book.title
      if(title != '' and title != book.title):
        self.update_title(title)
    else:
      book = models.UniqueBook(isbn=isbn,
                               title=title,
                               lastAdded = datetime.datetime.now(),
                               sellpage = '/sell?'+urllib.urlencode(
                                  {'isbn':isbn,'title':title}))
      book.put()
      self.book = book
      self.isbn = isbn
      self.title = title

  def update_date(self):
    self.book.lastAdded = datetime.datetime.now()
    self.book.put()

  
  def update_title(self,title):
    self.book.title = title
    self.title = title
    self.book.sellpage = self.sell_page()
    self.book.put()
  
  def sell_page(self):
    return '/sell?'+urllib.urlencode({'isbn':self.isbn,'title':self.title})
