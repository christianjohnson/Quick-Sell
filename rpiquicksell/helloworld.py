import os
import cgi
import datetime
import urllib
import wsgiref.handlers

from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class Greeting(db.Model):
	author = db.UserProperty()
	content = db.StringProperty(multiline=True)
	date = db.DateTimeProperty(auto_now_add=True)

def guestbook_key(guestbook_name=None):
	return db.Key.from_path('Guestbook', guestbook_name or 'default_guestbook')

class MainPage(webapp.RequestHandler):
	def get(self):
		guestbook_name=self.request.get('guestbook_name')
		greetings_query = Greeting.all().ancestor(
			guestbook_key(guestbook_name)).order('-date')
		greetings = greetings_query.fetch(10)

		if users.get_current_user():
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'

		template_values = {
		'greetings': greetings,
		'url': url,
		'url_linktext': url_linktext,
		'guestbook_name':guestbook_name,
		'guestbook_name_url':urllib.urlencode({'guestbook_name':guestbook_name}),
		}

		path = os.path.join(os.path.dirname(__file__), 'html/index.html')
		self.response.out.write(template.render(path, template_values))

class Guestbook(webapp.RequestHandler):
	def post(self):
		guestbook_name = self.request.get('guestbook_name')
		greeting = Greeting(parent=guestbook_key(guestbook_name))

		if users.get_current_user():
			greeting.author = users.get_current_user()

		greeting.content = self.request.get('content')
		greeting.put()
		self.redirect('/?' +urllib.urlencode({'guestbook_name':guestbook_name}))

application = webapp.WSGIApplication([('/', MainPage),
										('/sign',Guestbook)],debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()

