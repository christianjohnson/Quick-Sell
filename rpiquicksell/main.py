#!/usr/bin/env python

import jinja2
import os
import webapp2

from google.appengine.api import users

import models

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MainHandler(webapp2.RequestHandler):
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
      'url_linktext': url_linktext
    }

    template = jinja_environment.get_template('index.html')
    self.response.out.write(template.render(template_values))
    
class BrowseBooks(webapp2.RequestHandler):
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

    template = jinja_environment.get_template('browse.html')
    self.response.out.write(template.render(template_values))

class SellBooks(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user:
  		url = users.create_logout_url(self.request.uri)
  		url_linktext = 'Logout'
  		user = users.get_current_user()
    else:
      self.redirect(users.create_login_url(self.request.uri))

    template_values = {
      'user': user,
      'url_linktext': url_linktext,
    }

    template = jinja_environment.get_template('sell.html')
    self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/browse', BrowseBooks),
                               ('/sell', SellBooks)], 
                               debug=True)

