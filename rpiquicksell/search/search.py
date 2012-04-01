import models
from isbndb.isbndb import isbndb
from isbndb.isbn import ISBN
import datetime



class Search(object):
  def __init__(self,search_string,querysize = 10):
    self.offset = 0
    self.limit = querysize

    self.isbn = ISBN(search_string);
    self.isbn.to_isbn13()
    if self.isbn.valid_isbn13():
      remote_books = models.Book.all().filter('isbn =',self.isbn.format('')).filter('is_local =', False).filter('date >=',datetime.datetime.now()-datetime.timedelta(10)).order('-date').get()
      if not remote_books:
        isbndb_query = isbndb()
        isbnbooks = isbndb_query.searchBook(isbn=self.isbn.format(''))
        for book in isbnbooks:
          book.add_to_database(self.isbn.format(''))
      
      self.local_books = models.Book.all().filter('isbn =', self.isbn.format('')).filter('is_local =', True).order('-date')
      self.remote_books = models.Book.all().filter('isbn =', self.isbn.format('')).filter('is_local =', False).order('-date')
    
    else:
      self.local_books = models.Book.all()
      self.remote_books = models.Book.all()
  
  def next(self):
    self.offset+=self.limit
    return (self.local_books.fetch(self.limit,self.offset-self.limit),
            self.remote_books.fetch(self.limit,self.offset-self.limit))
    
    

