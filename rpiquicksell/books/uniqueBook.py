import models
import datetime
import urllib

class UniqueBook(object):
  
  def __init__(self, isbn, title='', requery=True):
    book = models.UniqueBook.all().filter('isbn =',isbn).get()
    if book:
      self.book = book
      self.isbn = book.isbn
      self.title = book.title
      self.found = True
      self.requery = requery
      if(title != '' and title != book.title):
        self.update_title(title)
    else:
      self.found = False
      self.book = None
      self.isbn = isbn
      self.title = title
      self.requery = requery
  
  def create_book(self,title,requery):
    if(self.found):
      self.title = title
      self.requery = requery
      self.book.title = title
      self.book.requery = requery
      self.book.put()
      return
    self.title = title
    self.book = models.UniqueBook(isbn = self.isbn,
                             title = self.title,
                             lastAdded = datetime.datetime.now(),
                             sellpage = self.sell_page(),
                             requery = requery)
    self.book.put()

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


  def get_local_books(self):
    return self.book.books.filter('is_local =',True).filter('sold_date =', None).order('-date')

  def get_remote_books(self):
    return self.book.books.filter('is_local =',False).order('-date')

