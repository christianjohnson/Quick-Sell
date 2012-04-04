from xml.dom.minidom import parseString
import urllib
from book import Book
import book

class isbndb:
  def __init__(self,isbndb_access_key='X5ANT93D'):
    self.bookSite = Website('http://isbndb.com/api/books.xml?',isbndb_access_key)

  def searchBook(self, isbn=None, title=None, combined=None, full=None):
    """Searches for a book on isbndb.com using one of the above 
    arguments (ISBNDB only allows for one, if you call it with multiple 
    you will get the most discriminative in the following order
    isbn > title combined > full). 
    Returns a list of 0 or more book objects depending on the request.
    
    isbn: Searches for the specific book that has the ISBN given.
    title: text search only the titles of books
    combined: text search titles, authors, and publisher name
    full: text search titles, publisher name, summary, notes, awards information, etc

    Text searches must be properly formed prior to
    passing to this method.

    Because text searches can return a large number of 
    results, only the first page (10) results will
    be passed as a return from this function."""
    
    
    xmlResponse = None
    if(isbn):
      xmlResponse = self.bookSite.searchISBN(isbn)
    
    if(title and not xmlResponse):
      xmlResponse = self.bookSite.searchTitle(title)
    
    if(combined and not xmlResponse):
      xmlResponse = self.bookSite.searchCombined(combined)
    
    if(full and not xmlResponse):
      xmlResponse = self.bookSite.searchFull(full)
      
    print xmlResponse
    books = []
    parsedXML = parseString(xmlResponse)
    bookParser = book.BookXMLParser()
    
    booksData = parsedXML.getElementsByTagName('BookData')
    print len(booksData)
    for bookData in booksData:
      books.append(bookParser.parse(bookData))
    return books

class Website:
  def __init__(self,site,accesskey):
    self.site = site
    self.accessKey = accesskey

  def __str__(self):
    return self.site+'access_key='+self.accessKey+'&results=texts,details,prices&'

  def searchISBN(self, isbn):
    return self.search('isbn',isbn)

  def searchTitle(self, title):
    return self.search('title',title)

  def searchCombined(self, combined):
    return self.search('combined',combined)
  
  def searchFull(self, full):
    return self.search('full',full)

  def search(self,indextype,value):
    url = str(self)+'index1='+indextype+'&value1='+value
    site = urllib.urlopen(url)
    return site.read()


if __name__ == '__main__':
  isbnsearch = isbndb()
  books = isbnsearch.searchBook(isbn='9781558607873')
  for book in books:
    print str(book)

