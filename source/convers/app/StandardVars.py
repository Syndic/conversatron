import cgi
try:
	import cgitb;
	cgitb.enable()
except ImportError,e: pass

import Cookie
from os import environ

import ConvDB

import buff
import User

__all__ = ['cookies', 'form', 'db', 'user', 'buff']

# Install the buffered output manager
buff = buff.Out()

# Get request cookies
cookies = Cookie.SimpleCookie(environ.get('HTTP_COOKIE',''))

# Get request form+querystring data
form = cgi.FieldStorage()

# Open a database connection
db = ConvDB.Init()

# Retreive the current viewing user
user = User.Current(db)
