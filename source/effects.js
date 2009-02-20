var Class = {
  create: function() {
    return function() { 
      this.initialize.apply(this, arguments);
    }
  }
}

Function.prototype.bind = function(object) {
  var method = this;
  return function() {
    method.apply(object, arguments);
  }
}


var Effect = new Object();

Effect.Fade = Class.create();
Effect.Fade.prototype = {
  initialize: function(element) {
    this.element = $(element);
    this.start  = 100;
    this.finish = 0;
    this.current = this.start;
    this.fade();
  },
  
  fade: function() {
    if (this.isFinished()) { this.element.style.display = 'none'; return; }
    if (this.timer) clearTimeout(this.timer);
    this.setOpacity(this.element, this.current);
    this.current -= 10;
    this.timer = setTimeout(this.fade.bind(this), 50);
  },
  
  isFinished: function() {
    return this.current <= this.finish;
  },
  
  setOpacity: function(element, opacity) {
    opacity = (opacity == 100) ? 99.999 : opacity;
    element.style.filter = "alpha(opacity:"+opacity+")";
    element.style.opacity = opacity/100 /*//*/;
  }
}


Effect.Appear = Class.create();
Effect.Appear.prototype = {
  initialize: function(element) {
    this.element = $(element);
    this.start  = 0;
    this.finish = 100;
    this.current = this.start;
    this.fade();
  },
  
  fade: function() {
    if (this.isFinished()) return;
    if (this.timer) clearTimeout(this.timer);
    this.setOpacity(this.element, this.current);
    this.current += 10;
    this.timer = setTimeout(this.fade.bind(this), 50);
  },
  
  isFinished: function() {
    return this.current > this.finish;
  },
  
  setOpacity: function(element, opacity) {
    opacity = (opacity == 100) ? 99.999 : opacity;
    element.style.filter = "alpha(opacity:"+opacity+")";
    element.style.opacity = opacity/100 /*//*/;
    element.style.display = '';
  }
}