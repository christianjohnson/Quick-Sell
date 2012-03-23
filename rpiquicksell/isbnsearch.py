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

class Book(db.Model):
	isbn = db.IntegerProperty()
	content = db.StringProperty(multiline=True)
	date = db.DateTimeProperty(auto_now_add=True)

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

application = webapp.WSGIApplication([('/', MainPage),
										debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()

