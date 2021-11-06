#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/home/web/site-framework/")

from FlaskApp import app as application
application.secret_key = 'something super SUPER secret'
