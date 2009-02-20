#!/usr/bin/python

import ConvDB

from StandardVars import *

import web

print "Content-type: text/html\n"

search = form["search"].value
askees = db.loadObjects("select id,name,shortname,askee.retired from askee where askee.name like '%%%(search)s%%' or askee.shortname like '%%%(search)s%%' order by name" % {'search': search})

names = []
shorts = []
for askee in askees:
	names.append("\""+askee.name.replace("\"", "\\\"")+"\"")
	shorts.append("\""+askee.shortname.replace("\"", "\\\"")+"\"")

# javascript = "rpc_searchDone(\"" + search + "\",new Array(new Array("+",".join(names)+"),new Array("+",".join(shorts)+")))"

javascript = "rpc_searchDone(\"" + search + "\",[["+",".join(names)+"],["+",".join(shorts)+"]])"

print javascript
