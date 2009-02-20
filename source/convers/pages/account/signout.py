#!/usr/bin/env python

import web
from StandardVars import form
import User

# where to redirect to after signing out
target = form.getvalue('target','/')
User.SignOut()
web.Redirect(target)
