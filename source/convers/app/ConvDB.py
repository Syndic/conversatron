# Conversatron specific DB access
import dbops
import SuperHash
import stars

# ---------- General stuff --------
db = None
def Init():
	"Return a connected ObjectHash."
	
	global db
	if db is None:
		db = SuperHash.Database(dbops.user, dbops.database)
		
	return db;

def GetSlogan(bucket):
	"Get a slogan from the specified bucket. Buckets map to theme names."
	obj = db.loadObject('select slogan from slogan where theme="%s" order by rand() limit 1' % (bucket))
	if obj:
		return obj.slogan
	else:
		return ""

def GetUserTypes():
	sql = "select usertype,count(*) as count from user group by usertype order by usertype"
	return db.loadObjects(sql)


# ------- Some thread helper functions

def GetNumDeletedThreads():
	"Number of threads in the trashcan."
	return db.loadValue("select count(id) from thread where deleted='y'")
		
def GetNumNewThreads():
	"Number of unanswered threads."
	return db.loadValue("select count(id) from thread where active='n' and deleted='n'")
	
def GetNextPrev(id):
	sql = """
(select id, count
from thread
where
	thread.id < %(id)s and thread.active='y' and thread.deleted='n' 
order by id desc limit 1)
	union
(select id, count
from thread
where
	thread.id > %(id)s and thread.active='y' and thread.deleted='n' 
order by id asc limit 1)
"""
	return db.loadObjects(sql, {'id': id})
	
def GetNextThread(id):
	"Return the thread after this one."
	ob = db.loadObject("select id, count from thread where id > %s and active='y' and deleted='n' order by id limit 1", id)
	return ob
		
def GetPrevThread(id):
	"Return the thread after this one."
	ob = db.loadObject("select id, count from thread where id < %s and active='y' and deleted='n' order by id desc limit 1", id)
	return ob

def SetThreadProps(thread):
	messagecount = db.loadValue('select count(*) from entry where thread=%s and flag<>"s"', thread.id)
	
	followups = db.loadValue('select distinct "y" from entry where thread=%s and flag="s"', thread.id, default='n')
	
	thread.count = messagecount
	thread.followup = followups

def CacheThreadProps(threadid):
	"Set the cached reply count."
	
	# Unfortunately, MySQL <4.1 doesn't support subqueries, so we have to do this in 2 steps
	messagecount = db.loadValue('select count(*) from entry where thread=%s and flag<>"s"', threadid)
	
	followups = db.loadValue('select distinct "y" from entry where thread=%s and flag="s"', threadid, default='n')
	
	db.execute("update thread set count=%s , followup=%s where id=%s",
		(messagecount, followups, threadid))

def CacheThreadRating(threadid):
	"Update the cached rating for a thread."
	
	votecount = db.loadValue("select count(user) from rating where thread=%s", threadid)

	theRating = 0.0
	if votecount > 0:
		stats = db.loadObject("select sum(rating) as rating, min(rating) as min, max(rating) as max from rating where thread=%s",  threadid)
		
		theRating = stats.rating
			
		if votecount < stars.minvotes:
			theRating = theRating / votecount
		else: 
			theRating = (theRating - stats.min - stats.max) / (votecount-2)
	
	db.execute("update thread set rating=%s, numvotes=%s where id=%s",
		(theRating,votecount,threadid))


def GetActiveThreadList():
	return db.loadObjects("select id, archive, subject, count, time_format(whenis, '%l:%i %p') as time, weekday(whenis) as weekday, dayofyear(whenis) as yearday, followup, rating, numvotes from thread where active='y' and deleted='n' order by id desc")


def GetNewThreadList(order="chrono"):
	"Get all the unanswered threads."
	
	if order == "user":
		sort = "user.name"
	elif order == "subject":
		sort = "thread.subject"
	else:
		sort = "thread.id desc"
	
	op  = "select thread.id, thread.subject, user.name, thread.whenis from thread left join user on thread.user = user.id where thread.active='n' and thread.deleted='n' order by "+sort
	return db.loadObjects(op)

def GetDeletedThreadList():
	"Get deleted threads."
	op = "select thread.id, thread.subject, user.name, thread.whenis from thread left join user on thread.user = user.id where thread.deleted='y' order by thread.id desc"
	return db.loadObjects(op)


# ------ Some thread entry helper functions

def AddEntry(entry):
	"Add a thread entry to the db."

	entry._Store(db)
# 	Set the entry's order_id to its row id
	entry.oid=entry.id
	entry._Update(db)

def GetLatestEntryTime(thread_id):
	op = """select whenis from entry where entry.thread=%s order by whenis desc limit 1"""	
	return db.loadValue(op, (thread_id))

def GetThreadEntries(id, ShowSpecials=False, link=False, newerThan=None):
	"Return all entries with thread id. What a fucking ugly join, pardon my french."

	extraSQL = " and flag=' '"
	if ShowSpecials:
		extraSQL = ""
		
	if newerThan is not None:
		extraSQL = extraSQL + " and t.oid > " + str(newerThan) + " "
		
	linkSQL = ""
	if link:
		linkSQL =  "NULL as previd,NULL as nextid"
		
	op = """
select 
	t.id, t.emotion, t.body, t.addr, t.client, t.side, t.oid, t.flag, 
	time_format(t.whenis, '%%l:%%i %%p') as time, 

	user.name as uname, user.picture, user.gender,

	askee.name as aname, 
	askee.normpic, 
	askee.happypic, 
	askee.angrypic, 
	askee.sadpic, 
	askee.url,
	
	""" + linkSQL + """
from 
	entry as t 
	left join user on t.asker = user.id 
	left join askee on t.askee = askee.id 
where 
	t.thread = %(id)s 
	and t.oid <> 0 """ 
	+ extraSQL + """order by t.oid"""
	entries = db.loadObjects(op, {'id': id})
	
	# Add next/prev IDs into entry objects
	if link:
		num_entries = len(entries)
		for i in range(num_entries):
			if 1 < i:
				entries[i].previd = entries[i-1].id
				
			if 0 < i < num_entries-1:
				entries[i].nextid = entries[i+1].id
	
	return entries

	
def SwapEntries(id1, id2):
	"Swap the ids of two entries, for re-ordering purposes."
	
	try:
		db.execute("lock tables entry write")
		
		oid1 = db.loadValue("select oid from entry where id=%s", id1, default=0)
		if oid1 == 0: raise Exception
		
		oid2 = db.loadValue("select oid from entry where id=%s", id2, default=0)
		if oid2 == 0: raise Exception
				
		sql = "update entry set oid=%s where id=%s"
		db.execute(sql, (oid2, id1))
		db.execute(sql, (oid1, id2))
	except:
		pass
		
	db.execute("unlock tables")

# ------- Some user helper functions

def GetUserFavorites(user):
	"Return a list of user's favorite askees."
	if not user.favorites:
		return ()

	return db.loadObjects("select id, name from askee where id in (%s) order by name" % user.favorites)

def DeleteUser(id):
	"Delete a user from the database. PERMANENTLY."
	db.execute("delete from user where id="+str(id))
	db.execute("delete from rating where user="+str(id))
	db.execute("delete from pollvote where user="+str(id))


# ------- Some Askee helper functions

def GetNewestAskees(n=10):
	"Return a list of the most recently added askees."
	return db.loadObjects("select * from askee where retired = 'n' order by id desc limit %s" % (n))

def GetAskeeList():
	"Return a list of all active askees, sorted by category."	
	return db.loadObjects("select * from askee where retired = 'n' order by category, name")

def GetAskeeCategories():
	return db.loadObjects("select distinct category from askee order by category")

def GetAskeesForCategory(category):
	return db.loadObjects("select * from askee where category=%s order by name", category)	

def AskeeShortcutToID(shortcut):
	"Returns an askee ID based on shortcut."
	id = db.loadValue("select id from askee where shortname=%s", shortcut)
	if id is None:
		return None
	else:
		return int(id)

# -------- Some Rating helper functions

def AddRating(user, thread, rating):
	"Sets the users rating of the thread."
	
	old_rating = db.loadValue("select rating from rating where user=%s and thread=%s", 
		(user, thread))
	
	if old_rating is None:
		sql = "insert into rating (user, thread, rating) values (%(user)s, %(thread)s, %(rating)s)"
	else:
		sql = "update rating set rating=%(rating)s where user=%(user)s and thread=%(thread)s"

	db.execute(sql, {'user':user,'rating':rating,'thread':thread})

	CacheThreadRating(thread)


def GetRatingList(thread):
	"Gets list of users who have rated a thread"
	return db.loadObjects("select user.name, user.id, rating.rating, user.gender from user, rating where user.id=rating.user and rating.thread=%s order by rating desc, name asc", (thread))

def GetRatingHistory(user):
	return db.loadObjects("select thread.subject, rating.rating from thread,user,rating where rating.user=%s and user.id=rating.user and rating.thread=thread.id", (user))

def GetSelfRatingHistory(user):
	return db.loadObjects("select thread.subject, rating.rating from rating,thread where rating.user=%(user)s and thread.user=%(user)s and rating.thread=thread.id", 
		{'user':user})

# -------- Random statistics crap

def GetDailyUsers():
	op = "select id, name, lastip, lastused, gender from user where to_days(now()) - to_days(lastused) <= 1 order by id desc"

	return db.loadObjects(op)
