#!/usr/bin/env python

import os
import cgi
import datetime
import urllib
import wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import users
from google.appengine.ext.webapp import template

import models

class MainHandler(webapp.RequestHandler):
  def get(self):
    if users.get_current_user():
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
			user = users.get_current_user()
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'
      user = "Not Logged In"

    template_values = {
      'user': user,
      'url_linktext': url_linktext,
    }

    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))
    
class BrowseBooks(webapp.RequestHandler):
  def get(self):
    if users.get_current_user():
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
			user = users.get_current_user()
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'
      user = "Not Logged In"

    books = models.Book.all()
    
    template_values = {
      'user': user,
      'url_linktext': url_linktext,
      'books': books
    }
    
    book = models.Book(isbn=90909, title="Biology", price=50.03, description="Testing")
    
    book.put()

    path = os.path.join(os.path.dirname(__file__), 'books.html')
    self.response.out.write(template.render(path, template_values))

application = webapp.WSGIApplication([('/', MainHandler),
                                      ('/books', BrowseBooks),],
                                            debug=True)

def main():
  util.run_wsgi_app(application)

if __name__ == '__main__':
  main()
