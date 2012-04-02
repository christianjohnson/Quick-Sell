#!/usr/bin/env python

import jinja2
import cgi
import webapp2
import urllib

from google.appengine.api import users
from google.appengine.ext.db import BadValueError
from google.appengine.ext.webapp import template

import models
import logging

import os
import datetime

from isbndb.isbn import ISBN
import isbndb.isbndb

from search.search import Search as mySearch


#template.register_template_library('common.test_filter')

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MainHandler(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user:
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = "Log In"

    template_values = {
      'url' : url,
      'url_linktext': url_linktext
    }

    template = jinja_environment.get_template('html/index.html')
    self.response.out.write(template.render(template_values))
    
class BrowseBooks(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user:
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = "Log In"

    books = models.UniqueBook.all().order('-lastAdded')
    
    template_values = {
      'url' : url,
      'url_linktext': url_linktext,
      'books': books
    }

    template = jinja_environment.get_template('html/browse.html')
    self.response.out.write(template.render(template_values))
    
class BookInformation(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user:
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Welcome ' + user.nickname()
			user = users.get_current_user()
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'
      
    book_id = cgi.escape(self.request.get('id'))

    book = models.Book.get(book_id)

    template_values = {
      'url_linktext': url_linktext,
      'book': book
    }

    template = jinja_environment.get_template('html/bookinfo.html')
    self.response.out.write(template.render(template_values))

class SellBooks(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return
    else:  
  		url = users.create_logout_url(self.request.uri)
  		url_linktext = 'Welcome ' + user.nickname()
    
    if(self.request.get('badisbn')):
      template_values = {
          'url' : url,
          'url_linktext': url_linktext,
          'email' : user.email(),
          'badisbn' : True,
          'prev_title' : self.request.get('title'),
          'prev_price' : self.request.get('price')
      }
    else:
      template_values = {
          'url' : url,
          'url_linktext': url_linktext,
          'email' : user.email(),
          'badisbn' : False
      }

    template = jinja_environment.get_template('html/sell.html')
    self.response.out.write(template.render(template_values))
    
class SellBookForm(webapp2.RequestHandler):
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
    title = cgi.escape(self.request.get("title"))
    try:
      price = float(cgi.escape(self.request.get("price")))
    except BadValueError:
      price = 0.0

    condition = cgi.escape(self.request.get("condition"))
    
    if(text_isbn):
      book_to_insert = models.Book(isbn=text_isbn, 
                                 title=title, 
                                 price=price,
                                 condition=condition,
                                 user=user,
                                 is_local=True)
                                 
      book_to_insert.put()

      unique_book = models.UniqueBook.all().filter('isbn = ', text_isbn).get()
      if(unique_book):
        unique_book.lastAdded = book_to_insert.date
        unique_book.put()
      else:
        unique_book = models.UniqueBook(isbn=text_isbn,
                                        title=title,
                                        lastAdded=book_to_insert.date)
        unique_book.put()

      self.redirect("/browse")
    else:
      self.redirect('/sell?'+urllib.urlencode({'badisbn':True,'price':price,'title':title}))

class Search(webapp2.RequestHandler):
  def get(self):
    self.post()

  def post(self):
    
    user = users.get_current_user()

    if user:
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = "Log In"
    
    text_isbn = str(cgi.escape(self.request.get('search')))
    logging.info(text_isbn)
    try:
      search = mySearch(text_isbn)
      (search_type,arg1,arg2) = search.next()
    except:
      search_type = True
      arg1 = []
      arg2 = []

    if(search_type):
      books = arg1+arg2
      template_values = {
        'url' : url,
        'url_linktext': url_linktext,
        'books': books,
        'bookTitle':arg2[0].title,
        'text_isbn':text_isbn,
        'book_not_found':books==[]
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

    
app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/browse', BrowseBooks),
                               ('/bookInformation', BookInformation),
                               ('/sell', SellBooks),
                               ('/sellBook', SellBookForm),
                               ('/search',Search)], 
                               debug=True)

