#!/usr/bin/env python

"""main.py: The main handler of all website requests.  
            Each class handles a different URL."""

__author__      = "QuickSell Group (see GitHub)"
__copyright__   = "Copyright 2012, QuickSell"

import jinja2
import cgi
import webapp2
import urllib
import urlparse

from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.ext.db import BadValueError
from google.appengine.ext.webapp import template

import models
import logging

import os
import datetime

from isbndb.isbn import ISBN
import isbndb.isbndb

from search.search import Search as mySearch
from books.uniqueBook import UniqueBook

# this is the rendering enviornment (using Jinga2)
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class MainHandler(webapp2.RequestHandler):
  """Handles the main website.

       Args:
           webapp2.requestHandler: the webapp request to serve.
  """
  def get(self):
    user = users.get_current_user()
    if user:
      nickname = user.nickname()
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      nickname = ""
      url = users.create_login_url(self.request.uri)
      url_linktext = "Log In"

#the values passed to html
    template_values = {
      'url' : url,
      'url_linktext': url_linktext,
      'nickname' : nickname
    }

    template = jinja_environment.get_template('html/index.html')
    self.response.out.write(template.render(template_values))
    
class BrowseBooks(webapp2.RequestHandler):
  """Handles the BrowseBooks page.  Very similar to the MainHandler.

     Args:
         webapp2.requestHandler: the webapp request to serve.
  """
  def get(self):
    user = users.get_current_user()
    if user:
      nickname = user.nickname()
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      nickname = ""
      url = users.create_login_url(self.request.uri)
      url_linktext = "Log In"

    #get all books from database
    books = models.UniqueBook.all().order('-lastAdded')
    
    #the values passed to html
    template_values = {
      'url' : url,
      'url_linktext': url_linktext,
      'books': books,
      'nickname' : nickname
    }

    template = jinja_environment.get_template('html/browse.html')
    self.response.out.write(template.render(template_values))
    
class BookInformation(webapp2.RequestHandler):
  """The page where a specific book is clicked.

     Args:
         webapp2.requestHandler: the webapp request to serve.
  """
  def get(self):
    user = users.get_current_user()
    if user:
      nickname = user.nickname()
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      nickname = ""
      url = users.create_login_url(self.request.uri)
      url_linktext = "Log In"
      
    # fetches the book from the DB
    book_id = cgi.escape(self.request.get('id'))
    book = models.Book.get(book_id)
    
    emailed = cgi.escape(self.request.get("e"))
    
    try:
      emailed = int(emailed)
      if emailed == 1:
        text = 1
      else:
        text = None
    except:
      text = None

    #the values passed to html
    template_values = {
      'url_linktext': url_linktext,
      'url': url,
      'book': book,
      'email': book.user.email(),
      'nickname' : nickname,
      'text': text,
    }

    template = jinja_environment.get_template('html/bookinfo.html')
    self.response.out.write(template.render(template_values))

class EditBook(webapp2.RequestHandler):
  """Editing a book web page.

     Args:
         webapp2.requestHandler: the webapp request to serve.
  """
  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return
    else:  
          nickname = user.nickname()
          url = users.create_logout_url(self.request.uri)
          url_linktext = 'Logout'
    #get book from db
    book_id = cgi.escape(self.request.get('id'))
    book = models.Book.get(book_id)
    
    #check if correct user
    if not user == book.user:
      self.redirect("/browse")
      return   

    #the values passed to render the html      
    template_values = {
      'url_linktext': url_linktext,
      'book': book,
      'book_id': book_id,
      'isbn': book.unique.isbn,
      'title': book.unique.title,
      'email': book.user,
      'price': book.price,
      'condition': book.condition,
      'nickname' : nickname
    }

    template = jinja_environment.get_template('html/edit.html')
    self.response.out.write(template.render(template_values))

class ContactSeller(webapp2.RequestHandler):
  """Contact Seller.  Notice the post() function is 
     defined, not the get() function as in most handlers.

     Args:
         webapp2.requestHandler: the webapp request to serve.
  """
  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return

    #Form data
    book_id = cgi.escape(self.request.get("book_id"))
    book = models.Book.get(book_id)

    # if the book is valid, update it.
    if(book):
      mail.send_mail(sender="RPI QuickSell <rpiquicksell@rpiquicksell.appspotmail.com>",
                     to=book.user.email(),
                     subject=user.nickname() + " wants to purchase " + book.unique.title,
                     reply_to=user.email(),
                     body="""
      Hello:

      Your book, %s, has a potential buyer.  Please email them at: %s.

      The Quick Sell Team
      """ % (book.unique.title, user.email()))
    
    url_to_go = "/bookInformation?id=%s&e=1" % (book_id)
    logging.debug(str(book_id) + ", " + url_to_go)
    self.redirect(url_to_go)

class EditBookForm(webapp2.RequestHandler):
  """Handles the POST form when editing a book.  Notice the post() function is 
     defined, not the get() function as in most handlers.

     Args:
         webapp2.requestHandler: the webapp request to serve.
  """
  def post(self):
    user = users.get_current_user()
    if not user:
      nickname = user.nickname()
      self.redirect(users.create_login_url(self.request.uri))
      return

    #Form data
    try:
      isbn = ISBN(str(cgi.escape(self.request.get("isbn"))))
      isbn.to_isbn13()
      text_isbn = isbn.format('')
    except ValueError:
      text_isbn = None
    title = cgi.escape(self.request.get("title"))
    try:
      price = float(cgi.escape(self.request.get("price")))
    except BadValueError:
      price = 0.0

    condition = cgi.escape(self.request.get("condition"))
    
    book_id = cgi.escape(self.request.get("book_id"))
    book = models.Book.get(book_id)

    # if the book is valid, update it.
    if(book):
      book.price=price
      book.condition=condition
      book.title=title
      book.put()
      self.redirect("/user")
    else:
      self.redirect('/edit?'+urllib.urlencode({'badisbn':True,'price':price,'title':title}))

class RemoveBook(webapp2.RequestHandler):
  """Handles the removal book page.  Checks to see if the user is logged in and
     if so, removes it from the site.

     Args:
         webapp2.requestHandler: the webapp request to serve.
  """
  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return
    else:  
          nickname = user.nickname()
          url = users.create_logout_url(self.request.uri)
          url_linktext = 'Logout'
    
    #get book from db
    book_id = cgi.escape(self.request.get('id'))
    book = models.Book.get(book_id)
    
    #check correct user
    if not user == book.user:
      self.redirect("/browse")
      return   
      
    #the values passed to render the html      
    template_values = {
      'url_linktext': url_linktext,
      'url': url,
      'book': book,
      'book_id': book_id,
      'isbn': book.unique.isbn,
      'title': book.unique.title,
      'email': book.user,
      'price': book.price,
      'condition': book.condition,
      'nickname' : nickname
    }

    template = jinja_environment.get_template('html/remove.html')
    self.response.out.write(template.render(template_values))

class RemoveBookForm(webapp2.RequestHandler):
  """Handles the POST form to remove a book.

     Args:
         webapp2.requestHandler: the webapp request to serve.
  """
  def post(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return

    
    nickname = user.nickname()
    book_id = cgi.escape(self.request.get("book_id"))
    book = models.Book.get(book_id)
    
    success= cgi.escape(self.request.get("success"))
    #price= cgi.escape(self.request.get("price"))
    
    try:
      price = float(cgi.escape(self.request.get("price")))
    except BadValueError:
      price = 0.0
         
    if(book):
      if (success=="True"):
        book.sold_date=datetime.datetime.now()
        book.price=price
        book.put()
        self.redirect("/user")
      else:
        book.delete()
        self.redirect("/user")
    else:
      self.redirect("/user")
     
      
class SellBooks(webapp2.RequestHandler):
  """Handles the sell a book page.

     Args:
         webapp2.requestHandler: the webapp request to serve.
  """
  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return
    else:
      nickname = user.nickname()
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Log Out'
    
    #the values passed to render the html   
    template_values = {
      'url' : url,
      'url_linktext' : url_linktext,
      'email' : user.email(),
      'badisbn' : cgi.escape(self.request.get('badisbn')),
      'description' : cgi.escape(self.request.get('description')),
      'price' : cgi.escape(self.request.get('price')),
      'isbn' : cgi.escape(self.request.get('isbn')),
      'nickname' : nickname
    }

    template = jinja_environment.get_template('html/sell.html')
    self.response.out.write(template.render(template_values))
    
class SellBookForm(webapp2.RequestHandler):
  """Handles the POST form to sell a book.

     Args:
         webapp2.requestHandler: the webapp request to serve.
  """
  def post(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return

    #Form data
    try:
      isbn = ISBN(str(cgi.escape(self.request.get("isbn"))))
      isbn.to_isbn13()
      text_isbn = isbn.format('')
    except ValueError:
      text_isbn = None
    description = cgi.escape(self.request.get("description"))
    try:
      price = float(cgi.escape(self.request.get("price")))
    except BadValueError:
      price = 0.0

    condition = cgi.escape(self.request.get("condition"))
    
    if(text_isbn):
      # this will add the unique book if it doesn't exist
      search = mySearch(text_isbn)
      search.unique_book().update_date()
      
      book_to_insert = models.Book(unique=search.unique_book().book, 
                                 description=description, 
                                 price=price,
                                 condition=condition,
                                 user=user,
                                 is_local=True)
                                 
      book_to_insert.put()
      
      self.redirect("/browse")
    else:
      self.redirect('/sell?'+urllib.urlencode({'badisbn':True,'price':price,'description':description}))

class RecentSoldBooks(webapp2.RequestHandler):
  """Recent sold books page.

     Args:
         webapp2.requestHandler: the webapp request to serve.
  """
  def get(self):
    user = users.get_current_user()
    if user:
      nickname = user.nickname()
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      nickname = ""
      url = users.create_login_url(self.request.uri)
      url_linktext = "Log In"
      
      #get book from db
    books = models.Book.all().order('-sold_date')
    books
    
    #the values passed to html
    template_values = {
      'url' : url,
      'url_linktext': url_linktext,
      'books': books,
      'nickname' : nickname
    }

    template = jinja_environment.get_template('html/recentBook.html')
    self.response.out.write(template.render(template_values))
    
               
class UserProfile(webapp2.RequestHandler):
  """User profile page.

     Args:
         webapp2.requestHandler: the webapp request to serve.
  """
  def get(self):
    user = users.get_current_user()
    if user:
      nickname = user.nickname()
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      self.redirect(users.create_login_url(self.request.uri))
      return
      
    #get book db
    user_email = user.email()
    user_books = models.Book.all().filter('user = ', user)

    #the values passed to html
    template_values = {
      'url' : url,
      'url_linktext': url_linktext,
      'email' : user.email(),
      'nickname' : user.nickname(),
      'user_books' :user_books,
      'nickname' : nickname
    }

    template = jinja_environment.get_template('html/user.html')
    self.response.out.write(template.render(template_values))
    
    
class Search(webapp2.RequestHandler):
  """Handles the search functionality.

     Args:
         webapp2.requestHandler: the webapp request to serve.
  """
  def get(self):
    self.post()

  def post(self):
    user = users.get_current_user()

    if user:
      nickname = user.nickname()
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      nickname = ""
      url = users.create_login_url(self.request.uri)
      url_linktext = "Log In"
    
    text_isbn = str(cgi.escape(self.request.get('search')))
    #logging.info(text_isbn)
    #try:
    search = mySearch(text_isbn)
    (search_type,arg1,arg2) = search.next()
    #except:
    #  search_type = True
    #  arg1 = 'Not Found'
    #  arg2 = []

    if(search_type):
      books = arg2
      template_values = {
        'url' : url,
        'url_linktext': url_linktext,
        'books': books,
        'nickname' : nickname,
        'bookTitle':search.unique_book().title,
        'text_isbn':text_isbn,
        'book_not_found':False
      }

    
      template = jinja_environment.get_template('html/search.html')
      self.response.out.write(template.render(template_values))
    
    else:
      template_values = {
        'url' : url,
        'url_linktext' : url_linktext,
        'search_text' : arg1,
        'books' : arg2
      }
      template = jinja_environment.get_template('html/browse.html')
      self.response.out.write(template.render(template_values))

# this tells what urls to map to what classes.
    
app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/browse', BrowseBooks),
                               ('/bookInformation', BookInformation),
                               ('/sell', SellBooks),
                               ('/sellBook', SellBookForm),
                               ('/search',Search),
                               ('/user', UserProfile),
                               ('/edit', EditBook),
                               ('/editBook', EditBookForm),
                               ('/remove', RemoveBook),
                               ('/removeBook', RemoveBookForm),
                               ('/recentBook', RecentSoldBooks),
                               ('/contactSeller', ContactSeller)],
                               debug=True)

