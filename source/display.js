/* DOM & DHTML helper functions */
/* Version 0.9.1, 11 May 2005, Adamv.com */

// Looks up the given node by ID if a string is passed in,
// otherwise returns the given object.
// This lets functions work either with a node ID to look up
// or an already retreived node.

// Don't pass in anything other than strings or nodes.
function $(o) {
	if (typeof(o) == "string")
		return document.getElementById(o)
	else
		return o;
}

DOM = {
	// Remove all the children of the given node
	nuke: function(id){
		if (o=$(id)) {
			while(0 < o.childNodes.length)
				o.removeChild(o.childNodes[0]);
		}
	},
	
	before: function(id, node, nodeType){
		if (! (o=$(id))) return;
		
		if (typeof(node) == "string"){
			var newNode = document.createElement(nodeType || "div")
			newNode.innerHTML = node
			node = newNode
		}
		
		o.parentNode.insertBefore(node, o)
	},
	
	after: function(id, node, nodeType){
		if (! (o=$(id))) return;
		
		if (typeof(node) == "string"){
			var newNode = document.createElement(nodeType || "div")
			newNode.innerHTML = node
			node = newNode
		}
		
		o.parentNode.insertBefore(node, o.nextSibling)
	}
}

Display = {
	// Sets the visibility of the given node
	set_visible: function(id,visible){
		if (visible) Display.show(id); else Display.hide(id)
	},
	
	// Displays the given node by clearing the CSS display property
	// This resets display: to the default value for that element type
	show: function(id, style){
		if (style==null) style=""
		if (o=$(id)) o.style.display=style
	},
		
	// Hides the given node by setting CSS display: none
	hide: function(id){Display.show(id, "none")},
	
	// Toggle the visibility of the given node
	toggle: function(id){
		if (o=$(id)){
			(o.style.display == "none") ? Display.show(o) : Display.hide(o)
		}
	},
	
	// Sets the innerHTML of the given node, replacing its contents
	// with the given text parsed as HTML. Much more convenient
	// than manually creating a node tree with the DOM
	text: function(id, text){
		if (o=$(id)) o.innerHTML=text
	},
		
	// Enables the given node (useful for form elements.)
	enable: function(id){
		if (o=$(id)) o.disabled=false
	},
		
	// Disables the given node (useful for form elements.)
	disable: function(id){
		if (o=$(id)) o.disabled=true
	},

	background: function(id, color){
		if (o=$(id)) o.style.background=color
	}
}
