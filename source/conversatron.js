String.prototype.trim = function() {
  var x=this;
  x=x.replace(/^\s*(.*)/, "$1");
  x=x.replace(/(.*?)\s*$/, "$1");
  return x;
}

function CtrlEnterSubmit()
{
	if (this.event)
	{
		e = this.event;
		if ((e.keyCode==13) && (e.ctrlKey==true)) e.srcElement.form.submit();
	}
}

function showSignIn() {
	Display.hide('login_links')
	Display.show('login_form')
	return false;
}

function hideSignIn() {
	Display.show('login_links')
	Display.hide('login_form')
	return false;
}

Array.prototype.add = function() {
	for(i=0; i<arguments.length;i++)
	{
		var stuff = arguments[i];
		if (!stuff.length)
			this.push(stuff)
		else
		{
			for(j=0; j<stuff.length; j++){
				this.push(stuff[j]);
			}
		}
	}	
}

Array.Create = function() {
	var newArray = new Array();
	newArray.add.apply(newArray, arguments);
	return newArray;
}

/*
	Curries a function providing the first N arguments in advance.
*/
Function.prototype.partial = function() {
	var method = this;
	var _args = arguments;
	return function() {
			return method.apply(null, Array.Create(_args,arguments));
		}
}

Function.prototype.r_partial = function() {
	var method = this;
	var _args = arguments;
	return function() {
			return method.apply(null, Array.Create(arguments,_args));
		}
}

function foreach(stuff, f, f_mutate){
	if(f_mutate)
		for(i=0; i < stuff.length; i++){
			if ( f(f_mutate(stuff[i])) ) return;
		}
	else
		for(i=0; i < stuff.length; i++){
			if ( f(stuff[i]) ) return;
		}
}
