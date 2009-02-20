minvotes = 6

star_icons = {
	'gold_star': '<img src="/img/gs.gif" width=12 height=12 alt="Gold">',
	'silver_star': '<img src="/img/ss.gif" width=12 height=12 alt="Silver">',
	'bronze_star': '<img src="/img/bs.gif" width=12 height=12 alt="Bronze">',
	}


def RateThread(thread):
	star=''
	if int(thread.numvotes) >= minvotes:
		if thread.rating > 4.7:
			star = 'gold_star'
		elif thread.rating > 4.4:
			star = 'silver_star'
		elif thread.rating > 4.0:
			star = 'bronze_star'

	return star


def GetStarHtml(thread):
	star = '&nbsp;'

	starname = RateThread(thread)
	if starname: star = star_icons.get(starname, '&nbsp;')

	return star
