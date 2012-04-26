"""
search.py 

Defines a search object which can be used to retrieve books which
match the search string.

Retrieval indicates whether the search was for an isbn or for a 
book title.
"""
__author__      = "Quicksell Group (see Github)"
__copyright__   = "Copyright 2012, Quicksell"

import models
from isbndb.isbndb import isbndb
from isbndb.isbn import ISBN
from books.uniqueBook import UniqueBook
import datetime

import logging


class Search(object):
  """
  The Search object retrieves books from the local datastore
  as well as making calls to isbndb if necessary.

  Attributes:
    offset: an integer which is used to set the offset for the fetch commands
    limit: an integer, limits the number of books retrieved to it's value
    search_text: a string, the search string input to the class
    
    local_books: all books which are sold locally which fit the search text
    remote_books: all books which are sold externally which fit the search text
  """
  def __init__(self,search_string,querysize = 10):
    """
    Performs a search with the search_string, you should
    also set the querysize if you wish to see more than 10 
    results returned from search.next
    """
    self.offset = 0
    self.limit = querysize
    
    self.search_text = search_string
    isbn = ISBN(search_string)
    
    if isbn.valid():
      self.isbn = isbn
      self.isbn_search = True
      self.isbn.to_isbn13()
      self.unique = UniqueBook(self.isbn.format(''))
      remote_books = models.Book.all().filter('isbn =',self.isbn.format('')).filter('is_local =', False).filter('date >=',datetime.datetime.now()-datetime.timedelta(days=10)).order('-date').get()
      
      if not self.unique.found:
      
        isbndb_query = isbndb()
        
        logging.info('making query to isbndb')

        isbnbooks = isbndb_query.searchBook(isbn=self.isbn.format(''))
        
        logging.info('found %d books on isbndb'%len(isbnbooks))
        
        if(len(isbnbooks) == 0):
          self.unique.create_book('ISBN valid, but book not found')
        else:
          self.unique.create_book(isbnbooks[0].title)
        
        for book in isbnbooks:
          book.add_to_database(self.unique.book)

      self.local_books = self.unique.get_local_books()
      self.remote_books = self.unique.get_remote_books()
      
      logging.info('%d local  AND %d remote'%(self.local_books.count(),self.remote_books.count()))

    else:
      self.isbn_search = False
      
      arrsearch = self.search_text.split(' ')
      books = models.UniqueBook.all().order('-lastAdded')
      self.text_books = []
      for book in books:
        arrtitle = [x.lower() for x in book.title.split(' ')]

        if any([x.lower() in arrtitle for x in arrsearch]):
          self.text_books.append(book)       
  
  def unique_book(self):
    assert(self.isbn_search)
    return self.unique

  def next(self):
    """
    returns the next limit (as set in the init) books
    which match the search terms.  If the search was
    performed with an isbn, the first value in the
    tuple will be true, and user books are returned.

    Otherwise the first tuple
    is false, and the book types are unique_books.
    """
    self.offset+=self.limit
    if self.isbn_search:
      return (True,
              '',
              self.remote_books.fetch(self.limit)+self.local_books.fetch(self.limit))
    else:
      return (False,
              self.search_text,
              self.text_books)
    

