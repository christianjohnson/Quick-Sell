#!/usr/bin/env python

import jinja2
import cgi
import webapp2
import urllib
import urlparse

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
from books.uniqueBook import UniqueBook

import logging


#template.register_template_library('common.test_filter')

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MainHandler(webapp2.RequestHandler):
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

    template_values = {
      'url' : url,
      'url_linktext': url_linktext,
      'nickname' : nickname
    }

    template = jinja_environment.get_template('html/index.html')
    self.response.out.write(template.render(template_values))
    
class BrowseBooks(webapp2.RequestHandler):
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

    books = models.UniqueBook.all().order('-lastAdded')
    
    template_values = {
      'url' : url,
      'url_linktext': url_linktext,
      'books': books,
      'nickname' : nickname
    }

    template = jinja_environment.get_template('html/browse.html')
    self.response.out.write(template.render(template_values))
    
class BookInformation(webapp2.RequestHandler):
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
      
    book_id = cgi.escape(self.request.get('id'))

    book = models.Book.get(book_id)

    template_values = {
      'url_linktext': url_linktext,
      'url': url,
      'book': book,
      'email': book.user.email(),
      'nickname' : nickname
    }

    template = jinja_environment.get_template('html/bookinfo.html')
    self.response.out.write(template.render(template_values))

class EditBook(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return
    else:  
          nickname = user.nickname()
          url = users.create_logout_url(self.request.uri)
          url_linktext = 'Logout'
      
    book_id = cgi.escape(self.request.get('id'))
    book = models.Book.get(book_id)
    
    if not user == book.user:
      self.redirect("/browse")
      return   
      
    template_values = {
      'url_linktext': url_linktext,
      'book': book,
      'book_id': book_id,
      'isbn': book.isbn,
      'title': book.title,
      'email': book.user,
      'price': book.price,
      'condition': book.condition,
      'nickname' : nickname
    }

    template = jinja_environment.get_template('html/edit.html')
    self.response.out.write(template.render(template_values))

class EditBookForm(webapp2.RequestHandler):
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
    
    if(book):
      book.price=price
      book.condition=condition
      book.title=title
      '''book_to_update= models.Book(isbn=text_isbn, 
                                 title=title, 
                                 price=price,
                                 condition=condition,
                                 user=user,
                                 is_local=True)'''
      book.put()
      
      self.redirect("/user")
    else:
      self.redirect('/edit?'+urllib.urlencode({'badisbn':True,'price':price,'title':title}))

class RemoveBook(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return
    else:  
          nickname = user.nickname()
          url = users.create_logout_url(self.request.uri)
          url_linktext = 'Logout'
    
    
    book_id = cgi.escape(self.request.get('id'))
    book = models.Book.get(book_id)
    
    if not user == book.user:
      self.redirect("/browse")
      return   
      
    template_values = {
      'url_linktext': url_linktext,
      'url': url,
      'book': book,
      'book_id': book_id,
      'isbn': book.isbn,
      'title': book.title,
      'email': book.user,
      'price': book.price,
      'condition': book.condition,
      'nickname' : nickname
    }

    template = jinja_environment.get_template('html/remove.html')
    self.response.out.write(template.render(template_values))

class RemoveBookForm(webapp2.RequestHandler):
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
  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return
    else:
      nickname = user.nickname()
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Log Out'
    
    
    template_values = {
      'url' : url,
      'url_linktext' : url_linktext,
      'email' : user.email(),
      'badisbn' : cgi.escape(self.request.get('badisbn')),
      'title' : cgi.escape(self.request.get('title')),
      'price' : cgi.escape(self.request.get('price')),
      'isbn' : cgi.escape(self.request.get('isbn')),
      'nickname' : nickname
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
      
      search = mySearch(text_isbn) # this will add the unique book if it doesn't exist

      self.redirect("/browse")
    else:
      self.redirect('/sell?'+urllib.urlencode({'badisbn':True,'price':price,'title':title}))

class RecentSoldBooks(webapp2.RequestHandler):
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

    books = models.Book.all().order('-sold_date')
    books
    
    template_values = {
      'url' : url,
      'url_linktext': url_linktext,
      'books': books,
      'nickname' : nickname
    }

    template = jinja_environment.get_template('html/recentBook.html')
    self.response.out.write(template.render(template_values))
    
               
class UserProfile(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user:
      nickname = user.nickname()
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      self.redirect(users.create_login_url(self.request.uri))
      return
      

    user_email = user.email()
    user_books = models.Book.all().filter('user = ', user)

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
        'bookTitle':arg1,
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
                               ('/search',Search),
                               ('/user', UserProfile),
                               ('/edit', EditBook),
                               ('/editBook', EditBookForm),
                               ('/remove', RemoveBook),
                               ('/removeBook', RemoveBookForm),
                               ('/recentBook', RecentSoldBooks)],
                               debug=True)

