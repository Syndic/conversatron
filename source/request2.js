/* 
	XHR (XmlHttpRequest) Library
	Version 1.0
	6 Jun 2005 
	Adamv.com 
*/

var ReadyState = {
	Uninitialized: 0,
	Loading: 1,
	Loaded:2,
	Interactive:3,
	Complete: 4
}
	
var HttpStatus = {
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
	
var Cache = {
	Get: 1,
	GetCache: 2,
	GetNoCache: 3,
	FromCache: 4
}

var Method = {Get: "GET", Post: "POST", Put: "PUT", Delete: "DELETE"}

var XHR = {
	enabled: false,
	_get: null,
	_cache: new Object(),
	
	Init: function(){
		XHR._get = XHR._getXmlHttp()
		XHR.enabled = (XHR._get != null)
	},
	
	_getXmlHttp: function(){
	/*@cc_on @*//*@if (@_jscript_version >= 5)
		var progids=["Msxml2.XMLHTTP", "Microsoft.XMLHTTP"]
		for (i=0;i<progids.length;i++) {
			try { return new ActiveXObject(progids[i]) } 
			catch (e) {} 
		}
	@end @*/
		try { return new XMLHttpRequest();}
		catch (e2) {}

		return null;
	},

/*
	Params:
		url: The URL to request. Required.
		cache: Cache control. Defaults to Cache.Get.
		callback: onreadystatechange function, called when request is completed. Optional.
		method: HTTP method. Defaults to Method.Get.
*/
	get: function(params, callback_args){
		if (!XHR.enabled) throw "XHR: XmlHttpRequest not available.";
		
		var url = params.url;
		if (!url) throw "XHR: A URL must be specified";
				
		var cache = params.cache || Cache.Get;
		var method = params.method || Method.Get;
		var callback = params.callback;
		
		if ((cache == Cache.FromCache) || (cache == Cache.GetCache))
		{
			var in_cache = XHR.from_cache(url, callback, callback_args)
			if (in_cache || (cache == Cache.FromCache)) return in_cache;
		}
	
		
		if (cache == Cache.GetNoCache)
		{
			var sep = (-1 < url.indexOf("?")) ? "&" : "?"	
			url = url + sep + "__=" + encodeURIComponent((new Date()).toString());
		}
	
		// Only one request at a time, please
		if (XHR._get.readyState != ReadyState.Uninitialized) this._get.abort();
		
		XHR._get.open(method, url, true);

		XHR._get.onreadystatechange =  function() {
			if (XHR._get.readyState != ReadyState.Complete) return;
			
			if (cache == Cache.GetCached && XHR._get.status == HttpStatus.OK)
				XHR._cache[url] = XHR._get.responseText;
			
			callback.apply(null, Array.Create(XHR._get, callback_args));
		}
		
		XHR._get.send(params.body || null);
	},
	
	from_cache: function(url, callback, callback_args){
		var result = XHR._cache[url];
		
		if (result != null) {
			var response = new XHR.CachedResponse(result)
			callback(response, callback_args)
			return true
		}
		else
			return false
	},
	
	CachedResponse: function(response) {
		this.readyState = ReadyState.Complete
		this.status = HttpStatus.OK
		this.responseText = response
	}	
}

XHR.Init()


function getResponseProps(get){
	try {
		var s = get.getResponseHeader('X-Ajax-Props');
		if (s==null || s=="")
			return new Object()
		else
			return eval("o="+s)
	} catch (e) { return new Object() }
}
