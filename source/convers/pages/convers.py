#!/usr/bin/env python
#Display a thread, man!
import os
from StandardVars import *
import ConvDB
import stars

from BasicPage import BasicPage
import themes
import web

import words
from ReplyData import ReplyData

from Consts import Consts
import Thread

page_script = """
<script>
function search_url(search)
{
	return "search.py?search="+search
}

function got_search(get, index, search){
	if (get.readyState != ReadyState.Complete) return;
	if (get.status != HttpStatus.OK) return;
	
	var js = get.responseText;
	if (js)
	{
		var result = eval(js.trim());
		update_page(search, result)
	}
	
	Display.hide("spinner"+index)
	Display.enable("find-askee" + index)
}

function start_search(index)
{
	Display.show("spinner" + index)
	Display.disable("find-askee"+index)
	var term = document.forms.reply["askee-search"+index].value;
	
	XHR.get({
		url: search_url(term),
		callback: got_search
		},
		[index, term]);
}

function update_page(search, names)
{
	var blob = $("blob")
	if (blob)
	{
		DOM.nuke('blob')

		if (0 < names[0].length)
		{
			for(var i=0; i < names[0].length; i++)
			{
				var name = names[0][i];
				
				if (name.toLowerCase().indexOf(search.toLowerCase()) == -1)
				{
					name += " [<font color='#666666'><i>" + names[1][i] + "</i></font>]"
				}
				
				var aDiv = document.createElement("div");
				aDiv.innerHTML = name;
				blob.appendChild(aDiv);				
			}
		}
		else
		{
			var aDiv = document.createElement("div");
			aDiv.appendChild(document.createTextNode("(No results)"));
			blob.appendChild(aDiv);
		}
	}
}

// var request = new Request();
</script>
"""

buttons = Consts(
	MoreForms="moreforms_button",
	WriterReply="post_button",
	UserReply="user_reply")

class TopicPage(BasicPage):
	def __init__(self):
		BasicPage.__init__(self, post_buttons=buttons)
		
		self.DoNextPrev()
		self.GetThread()

		if user.IsReader() and not self.thread.isLive():
			web.GoHome()
			
		self.GetNumberOfForms()
		self.getReplies()
			
	def GetNumberOfForms(self):			
		self.numforms = int(form.getvalue("numforms",3))
		
		if self.postButton == buttons.MoreForms:
			try:
				moreforms = int(form.getvalue("moreforms", 0))
				self.numforms += self.moreforms
			except: pass

	def getReplies(self):
		self.replies = []
		self.anyReplies = 0
		self.anyErrors = 0
		
		if self.postButton == buttons.WriterReply:
			for num in range(self.numforms):
				reply = ReplyData(num)
				
				if reply.error: self.anyErrors = self.anyErrors + 1
				if not reply.isBlank: self.anyReplies = self.anyReplies + 1				
				self.replies.append(reply)
				
		elif self.postButton == buttons.UserReply:
			reply = ReplyData("")
			if not reply.isBlank: self.anyReplies = self.anyReplies + 1				
			self.replies.append(reply)
			
		else:
			self.replies = [ReplyData(i) for i in range(self.numforms)]

	def handleReplies(self):
		# If there are any errors then bail before touching the DB
		# Normal page processing will show errors in place.
		
		if self.anyErrors or not self.anyReplies: 
			return

		askeraddr = os.environ.get('REMOTE_ADDR', "Unknown")
		askerclient = os.environ.get('HTTP_USER_AGENT', "Unknown")
	
		for reply in self.replies:
			if reply.isBlank: continue
			
			body = reply.text
			if self.postButton == buttons.UserReply:
				body = body[:2048]
				body = web.SanitizeHTML(body)
		
			entry = db.newRow('entry',
					{
						'thread': self.thread.id,
						'whenis': db.datetime(),
						'asker': user.id,
						'body': web.NewlinestoBR(body),
						'addr': web.SanitizeHTML(askeraddr),
						'client': web.SanitizeHTML(askerclient)
					})
				
			if self.postButton == buttons.WriterReply:
				entry.askee = reply.idToUse
				entry.emotion = reply.emotion
				entry.side = reply.side
				
			elif self.postButton == buttons.UserReply:
				if 'suggest' in form:
					db.execute('delete from entry where flag<>" " and asker=%s and thread=%s', (entry.asker, entry.thread))
					
					entry.flag='s'
			
			ConvDB.AddEntry(entry)

		if self.postButton == buttons.WriterReply:
			self.thread.active = 'y'

		ConvDB.SetThreadProps(self.thread)
		self.thread.Update()
		web.RedirectToThread(self.thread)

	def run(self):
		if self.postButton in (buttons.WriterReply,buttons.UserReply):
			self.handleReplies()
		elif 'op' in form:
			self.handleOp()
			web.RedirectToThread(self.thread)
		
		self.javascript = page_script
		self.theme = themes.LoadTheme(self.thread.theme)
		self.theme.PrintThread(self)
			
	def handleOp(self):
		if not user.IsWriter(): return
		
		op = form.getvalue('op', None)
		value = form.getvalue('val', None)
				
		valid_values = ('y','n')
		valid_columns = {
			'save': 'archive',
			'close': 'locked',
			'open': 'open',
			'active': 'active',
			'done': 'done'
			}

		if (op in valid_columns) and (value in valid_values):
			self.thread[valid_columns[op]] = value
			self.thread.Update()
			
		elif op == 'clean':
			self.thread.Clean()
			self.thread.Update()

		else:
			return # no operations
		
		
	def PrintHeadLinks(self):
		link = """<link rel="%s" href="%s" title="%s" />\n"""
		print link % ('Top', '/', "Conversatron Current Posts")
		print link % ('Next', 'convers.py?next=' + str(self.thread.id), 'Next Topic')
		print link % ('Prev', 'convers.py?prev=' + str(self.thread.id), 'Previous Topic')


	def GetThread(self):
		if 'topic' not in form:
			web.GoHome()
			
		id = form.getvalue("topic")

		try:
			self.thread = Thread.Thread(id, True)
		except  Thread.NoTopicError, e:
			web.RedirectInFolder("/archive/%i.html" % (id))


	def DoNextPrev(self):
		row = None
		navigate = False
		
		if 'next' in form:
			row = ConvDB.GetNextThread(form.getvalue('next'))
			navigate = True
		elif 'prev' in form:
			row = ConvDB.GetPrevThread(form.getvalue('prev'))
			navigate = True

		if navigate:			
			if row is not None:
				web.RedirectInFolder('/convers.py?topic=%s&count=%s' % (row.id, row.count))
			else:
				web.GoHome()

	def ShowWriterStuff(self):
		if user.IsActive() and self.thread.isActive():
			self.ShowUserTalkback()
	
		if user.IsActive() and self.thread.isLive():
			self.ShowRateThisThread()
			
		if user.IsWriter():
			if self.thread.canWrite():
				self.ShowWriterReplies()	
			
			self.ShowThreadControl()

	def ShowUserTalkback(self):
		if self.thread.open =='y' or (self.thread.user == user.id and self.thread.locked == 'n'):
			self.theme.StartBox('You may participate in this discussion!')
			print '<form method="post" action="convers.py" name="openthread">'
			print '<input type="hidden" name="topic" value="' + str(self.thread.id) + '">'
			print '<textarea name="body" rows=10 cols=60 wrap=soft onkeydown="CtrlEnterSubmit()"></textarea><br>'
			print '<input type="submit" name="user_reply" value="Reply"></form>'
			self.theme.EndBox()
			print '<br>'
				
		# --- If talkback isn't explictly set, the user can still suggest a reply.
		elif (self.thread.user == user.id) and not self.thread.postedByAskee(): #self.thread.entries[0].aname == None):
			# ----- NOTE! If a writer starts a thread as an askee
			# then s/he can't jump in as an asker
			
			self.theme.StartBox('Follow-up Question')
			
			print ' <a href="/htmldocs/followups.html">Of course, we may choose to ignore it</a>.<br>'
			print '<form method="post" action="convers.py" name="followup">'
			print '<input type="hidden" name="topic" value="' + str(self.thread.id) + '">'
			print '<input type="hidden" name="suggest" value="1">'
			print '<textarea name="body" rows=10 cols=60 wrap=soft pponkeydown="CtrlEnterSubmit()">'

			# Look for a previous follow up and fill it in			
			for entry in self.thread.entries:
				if entry.flag == 's':
					body = entry.body.replace('<br>', '\n')
					print body
					break

			print'</textarea><br>'
			print '<input type="submit" name="user_reply" value="Reply"></form>'
			self.theme.EndBox()
			print '<br>'

	
	def ShowRatingDots(self):
		for i in range(5):
			print '<input type="radio" name="choice" value=%i>' % (i+1)


	def ShowRateThisThread(self):
		print '<br>'
		print '<div>'

		print '<form method="post" action="rate.py" name="rateform">'
		
		print '<input type="hidden" name="topic" value="' + str(self.thread.id) + '">'
		print '<input type="hidden" name="next" value="n">'

		print '<table>'
		print '''
<tr>
<td><img src="/img/2000-rate.gif" align="absmiddle"></td>
<td align=center><img src="/img/2000-ratethis.gif" width=113 height=21></td>
<td></td>
</tr>
'''
		print '<tr>'
		print '<td valign=bottom>Not Funny</td>'
		print '''
<td align=center>
<img src="/img/2000-rating.gif" width=108 height=10><br>
'''

		for i in range(5):
			print '<input type="radio" name="choice" value=%i>' % (i+1)
		
		print '</td>'
		print '<td valign=bottom>Funny</td>'
		print '</tr>'
		print '<tr><td colspan=3 align=center>'
		print '''
<br>
<input name=rate type="submit" value="Rate!">&nbsp;
<input name=ratenext type="submit" value="Rate, view next" onclick="document.rateform.next.value=\'y\';">
'''
		print '</td></tr>'
		print '</table>'
		print '</form>'	
	
		if self.thread.numvotes:
			print 'Average rating: '+str(self.thread.rating)
			
			if user.usertype > 1:
				print '&nbsp;&nbsp;&nbsp;Total votes: '+str(self.thread.numvotes)

				print '&nbsp;&nbsp;&nbsp;[<a href="threadratings.py?thread=' + str(self.thread.id) + '" target="window">View Ratings</a>]'

				print '<br>'

				remaining = stars.minvotes - int(self.thread.numvotes)
				if remaining > 0:
					print "%s more %s must rate this thread for it to be ranked" % (
						remaining, words.ChooseWord(remaining,'person','people'))
			
				print '<br>'
				print '<br>'
	
		print '</div><br>'
	

	def ShowWriterReplies(self):
		self.theme.StartBox('Post a Reply')
		
		if self.anyErrors:
			print '<font color="red">There were errors in your post.</font><br>'
		
		print '<form method="post" action="convers.py" name=reply>'
		print '<a name="writers"></a>'
		print '<input type="hidden" name="topic" value="' + str(self.thread.id) + '">'
		print '<input type="hidden" name="numforms" value="'+str(self.numforms)+'">'
		
		for reply in self.replies:
			self.ShowEditForm(reply, user.Favorites())
		
		print 'Please quickly proofread your reply. Thank you. <input type="submit" name="post_button" value="Reply"><br><br>'

		print "I need <input type=text name='moreforms' value='4' size=2> more forms. <input type='submit' name='moreforms_button' value='Get some more'><br>"

		print "</form>"
	
		self.theme.EndBox()
		print '<br>'
	

	def ShowThreadControl(self):
		self.theme.StartBox('Thread Control')
		
		if self.thread.deleted == 'y':
			print '<a href="/mans/threads.py?op=undelete&id=' + str(self.thread.id) + '">Undelete this thread</a><br><br>'
		else:
			print '<a href="/mans/threads.py?op=delete&id=' + str(self.thread.id) + '">Delete this thread</a><br><br>'
		
		print '<b>Thread attributes:</b> (click to toggle)<br>'
		
		print 'When thread expires: ',
		if self.thread.archive == 'y':
			print '<a href="convers.py?topic=' + str(self.thread.id) + '&op=save&val=n">Will be archived</a><br>'
		else:
			print '<a href="convers.py?topic=' + str(self.thread.id) + '&op=save&val=y">Will be deleted</a><br>'
				
		print 'Group participation: ',
		if self.thread.open == 'y':
			print '<a href="convers.py?topic=' + str(self.thread.id) + '&op=open&val=n">enabled</a><br>'
		else:
			print '<a href="convers.py?topic=' + str(self.thread.id) + '&op=open&val=y">disabled</a><br>'
		
		print 'Visibility: ',
		if self.thread.active == 'y':
			print '<a href="convers.py?topic=' + str(self.thread.id) + '&op=active&val=n">visible to users</a><br>'
		else:
			print '<a href="convers.py?topic=' + str(self.thread.id) + '&op=active&val=y">visible to writers</a><br>'
		
		if self.thread.done == 'y':
			print '<a href="convers.py?topic=' + str(self.thread.id) + '&op=done&val=n"><br>Unlock thread</a><br>'
		else:
			print '<a href="convers.py?topic=' + str(self.thread.id) + '&op=done&val=y"><br>Lock thread</a> - <a href="convers.py?topic=' + str(self.thread.id) + '&op=clean">Lock and bust ghosts</a><br>'
			
		self.theme.EndBox()
		

	def ShowEditForm(self, reply, favs):
		emotions = (
			('Normal', 'n'), 
			('Happy', 'h'), 
			('Angry','a'), 
			('Sad', 's'))
	
		data = {}
		data['suffix'] = reply.replyIndex
		data['shortname'] = web.SanitizeHTML(reply.shortname)
		data['text'] = web.SanitizeHTML(reply.text)
		data['askee'] = reply.askeeid
		
		if reply.side=='r': 
			data['onRight'] = " checked "
		else:
			data['onRight'] = ""

		if reply.error:
			print '<font color="red">%s</font><br>' % (reply.error)

		print """From:&nbsp;<input name="shortname%(suffix)s" type="text" size=12 maxlength=12 value="%(shortname)s">""" % data

		print """<a href="askeeman2.py?op=frameset&mode=browse&formtarget=%(suffix)s" target="window">Browse...</a>""" % data

		web.PrintFavoriteSelector(favs, 'askee'+str(data['suffix']), str(data['askee']))
		web.HtmlSelect(emotions, 'emotion'+str(data['suffix']), reply.emotion)
		
		print """ Right:&nbsp;<input name="onright%(suffix)s" type="checkbox" %(onRight)s><br>""" % data
		
		print """
<div class='find-askee' style="padding:5px 0px;">
Search: <input type='text' name='askee-search%(suffix)s' class='find-askee' size='12' maxlength='12'> <input type='button' id='find-askee%(suffix)s' class='action' onclick='start_search("%(suffix)s")' value="Find...">
<img src="/img/loading.gif" align="absmiddle" style="display: none;" class="spinner" id="spinner%(suffix)s">
<div class="search-results" id="blob"></div>
</div>
""" % data
		
		print """<textarea onkeydown="CtrlEnterSubmit()" name="body%(suffix)s" rows=10 cols=60 wrap=soft>%(text)s</textarea><br><br>
""" % data


def main():
	page = TopicPage()
	page.run()

main()
