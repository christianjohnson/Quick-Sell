import models
from isbndb.isbndb import isbndb
from isbndb.isbn import ISBN
import datetime



class Search(object):
  def __init__(self,search_string,querysize = 10):
    self.offset = 0
    self.limit = querysize
    
    self.search_text = search_string
    isbn = ISBN(search_string)
    
    if isbn.valid():
      self.isbn = isbn
      self.isbn_search = True
      self.isbn.to_isbn13()
      remote_books = models.Book.all().filter('isbn =',self.isbn.format('')).filter('is_local =', False).filter('date >=',datetime.datetime.now()-datetime.timedelta(10)).order('-date').get()
      
      if not remote_books:
        isbndb_query = isbndb()
        isbnbooks = isbndb_query.searchBook(isbn=self.isbn.format(''))
        
        for book in isbnbooks:
          book.add_to_database(self.isbn.format(''))
      
      self.local_books = models.Book.all().filter('isbn =', self.isbn.format('')).filter('is_local =', True).order('-date')
      self.remote_books = models.Book.all().filter('isbn =', self.isbn.format('')).filter('is_local =', False).order('-date')
    
    else:
      self.isbn_search = False
      
      arrsearch = self.search_text.split(' ')
      books = models.UniqueBook.all().order('-lastAdded')
      self.text_books = []
      for book in books:
        arrtitle = book.title.split(' ')
        if any([x in arrtitle for x in arrsearch]):
          self.text_books.append(book)       
  
  def next(self):
    self.offset+=self.limit
    if self.isbn_search:
      return (True,
              self.local_books.fetch(self.limit,self.offset-self.limit),
              self.remote_books.fetch(self.limit,self.offset-self.limit))
    else:
      return (False,
              self.search_text,
              self.text_books)
    

