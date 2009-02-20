/* XmlHttpRequest library */
/* Version 0.9.2.2, 6 May 2005, Adamv.com */
function _getXmlHttp()
{
/*@cc_on @*/
/*@if (@_jscript_version >= 5)
	var progids=["Msxml2.XMLHTTP", "Microsoft.XMLHTTP"]
	for (i in progids) {
		try { return new ActiveXObject(progids[i]) }
		catch (e) {}
	}
@end @*/
	try { return new XMLHttpRequest();}
	catch (e2) {return null; }
}

function CachedResponse(response) {
	this.readyState = ReadyState.Complete
	this.status = HttpStatus.OK
	this.responseText = response
}

function getResponseProps(get){
	try {
		var s = get.getResponseHeader('X-Ajax-Props');
		if (s==null || s=="")
			return new Object()
		else
			return eval("o="+s)
	} catch (e) { return new Object() }
}

ReadyState = {
	Uninitialized: 0,
	Loading: 1,
	Loaded:2,
	Interactive:3,
	Complete: 4
	}
	
HttpStatus = {
	OK: 200,
	
	Created: 201,
	Accepted: 202,
	NoContent: 204,
	
	BadRequest: 400,
	Forbidden: 403,
	NotFound: 404,
	Gone: 410,
	
	ServerError: 500
	}

function Request_from_cache(url, f_change) {
	var result = this._cache[url];
	
	if (result != null) {
		var response = new CachedResponse(result)
		f_change(response)
		return true
	}
	else
		return false
}

function Request_cached_get(url, f_change) {
	if (!this.FromCache(url, f_change)){
		var request = this
		this.Get(url,
			/* Cache results if request completed */
			function(x){
				if ((x.readyState==ReadyState.Complete)&&(x.status==HttpStatus.OK))
				{request._cache[url]=x.responseText}
				f_change(x)
			},
			"GET")
	}
}

function Request_get(url, f_change, method) {
	if (!this._get) return;
	
	method = method || "GET"

	if (this._get.readyState != ReadyState.Uninitialized)
		this._get.abort() 
	
	this._get.open(method, url, true);
	
	if (f_change != null) {
		var _get = this._get;
		this._get.onreadystatechange = function(){f_change(_get);}
	}
	this._get.send(null);
}

function Request_get_no_cache(url, f_change, method){
	var sep = (-1 < url.indexOf("?")) ? "&" : "?"	
	var newurl = url + sep + "__=" + encodeURIComponent((new Date()).toString());
	return this.Get(newurl, f_change, method);
}

function Request() {
	this.Get = Request_get
	this.GetNoCache = Request_get_no_cache
	this.CachedGet = Request_cached_get
	this.FromCache = Request_from_cache
	
	this.Use = function(){return this._get!=null}
	this.Cancel = function(){if (this._get) this._get.abort();}
	this._cache = new Object();
	
	this._get = _getXmlHttp();
	if (this._get == null) return;
}
