import models
from isbndb.isbndb import isbndb
from isbndb.isbn import ISBN
from books.uniqueBook import UniqueBook
import datetime

import logging

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
        
        logging.info('making query to isbndb')

        isbnbooks = isbndb_query.searchBook(isbn=self.isbn.format(''))
        
        logging.info('found %d books on isbndb'%len(isbnbooks))
        
        if(len(isbnbooks) == 0):
          UniqueBook(self.isbn.format(''),'ISBN is valid, but book not found on isbndb')
        else:
          UniqueBook(self.isbn.format(''),isbnbooks[0].title)
        for book in isbnbooks:
          book.add_to_database(self.isbn.format(''))
      else:
        uniquebook = UniqueBook(self.isbn.format(''),remote_books.title)
        self.title = uniquebook.title

      self.local_books = models.Book.all().filter('isbn =', self.isbn.format('')).filter('is_local =', True).order('-date')
      self.remote_books = models.Book.all().filter('isbn =', self.isbn.format('')).filter('is_local =', False).order('-date')
    
    else:
      self.isbn_search = False
      
      arrsearch = self.search_text.split(' ')
      books = models.UniqueBook.all().order('-lastAdded')
      self.text_books = []
      for book in books:
        arrtitle = [x.lower() for x in book.title.split(' ')]

        if any([x.lower() in arrtitle for x in arrsearch]):
          self.text_books.append(book)       
  
  def next(self):
    self.offset+=self.limit
    if self.isbn_search:
      return (True,
              '',
              self.remote_books.fetch(self.limit,self.offset-self.limit)+self.local_books.fetch(self.limit,self.offset-self.limit))
    else:
      return (False,
              self.search_text,
              self.text_books)
    

