var _get = null;
var _search_cache = new Object();

String.prototype.trim = function() {
  var x=this;
  x=x.replace(/^\s*(.*)/, "$1");
  x=x.replace(/(.*?)\s*$/, "$1");
  return x;
}

function nukeNode(aNode)
{
 	while(0 < aNode.childNodes.length)
 	{
		aNode.removeChild(aNode.childNodes[0]);
	}
}

function setDisplay(nodeName, newDisplay)
{
	var aStatus = document.getElementById(nodeName)
	if (aStatus) 
	{
		aStatus.style.display = newDisplay;
	}
}

function getXmlHttp()
{
	var x = null;

/*@cc_on @*/
/*@if (@_jscript_version >= 5)
	try { x = new ActiveXObject("Msxml2.XMLHTTP") }
	catch (e)
	{
		try { x = new ActiveXObject("Microsoft.XMLHTTP") }
		catch(e2)
		{
			x = null;
		}
	}
@end @*/
	if ((!x) && typeof XMLHttpRequest != "undefined")
	{
		x = new XMLHttpRequest();
	}
	
	return x;
}

function rpc_searchDone(search, results)
{
	_search_cache[search] = results;
	update_page(search, results);
}

function update_page(search, names)
{
	var blob = document.getElementById("blob")
	if (blob)
	{
		nukeNode(blob)

		if (0 < names[0].length)
		{
			for(var i=0; i<names[0].length; i++)
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

function _get_change()
{
	if (_get.readyState != 4) return;

	if (_get.status == 200)
	{
		var js = _get.responseText;
		if (js)
		{
			eval(js.trim());
		}
	}
	
	setDisplay("status", "none");
}

function request_search(search)
{
	if (_get && _get.readyState!=0) 
	{
		_get.abort() 
	}
	
	var cached = _search_cache[search]
	if (!cached)
	{	
		_get = getXmlHttp();
		if (_get)
		{
			setDisplay("status", "block");
		
			_get.open("GET", "search.py?search="+search, true);
			_get.onreadystatechange = _get_change;
			_get.send(null);
		}
	}
	else
	{
		update_page(search, cached)
	}
}
