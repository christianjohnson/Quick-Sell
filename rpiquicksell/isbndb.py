import xml.dom.minidom
import urllib
import book

class isbndb:
  def __init__(self,isbndb_access_key='X5ANT93D'):
    self.bookSite = 'http://isbndb.com/api/books.xml?'
    self.access_key = isbndb_access_key

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
    
    url = self.bookSite+'access_key='+self.access_key+'&results=texts,details,prices&'
    if(isbn):
      url+='&index1=isbn&value1='+isbn
      xmlResponse = urllib.urlopen(url).read()
    elif(title):
      url+='&index1=title&value1='+title
      xmlResponse = urllib.urlopen(url).read()
    elif(combined):
      url+='&index1=combined&value1='+combined
      xmlResponse = urllib.urlopen(url).read()
    elif(full):
      url+='&index1=full&value1='+full
      xmlResponse = urllib.urlopen(url).read()
    else:
      return []

    books = []
    booksData = xml.dom.minidom.parseString(xmlResponse).getElementsByTagName('BookData')
    for bookData in booksData:
      books.append(book.Book(bookData))
    return books
