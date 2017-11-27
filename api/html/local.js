(function() {

var error = function(url, callback) {
        console.log('Fetch failed, trying again in 1 second');
	show('Server appears to be offline..');
        setTimeout(function() {
            fetch(url, callback);
        }, 1000);
};

var fetch = function(url, callback) {
    var oReq = new XMLHttpRequest();
    oReq.addEventListener('load', function() {
	var cType = oReq.getResponseHeader('content-type').split(';')[0];
	var json = {};
	if (cType.indexOf('json') > -1) {
		try {
			json = JSON.parse(this.responseText);
		} catch (e) {
			return error(url, callback);
		}
	}
	if (cType.indexOf('text') > -1) {
		json = this.responseText;
	}
        callback(json);
    });
    oReq.addEventListener('error', function() {
	error(url, callback);
    });
    oReq.open('GET', url);
    oReq.send();
};

var status = function(callback) {
    fetch('./lights/status', callback); 
};

var update = function() {
    status(function(json) {
        if (json && json.lights && json.pins) {
            Object.keys(json).forEach(function(sub) {
                Object.keys(json[sub]).forEach(function(key) {
                    var id = sub + '_' + key;
                    var el = document.getElementById(id);
                    if (el) {
                        el.className = json[sub][key];
                    }
                });
                if (sub === 'temps') {
                    var temps = json.temps;
                    document.querySelector('#temps span').innerHTML = temps.F + '&deg; F / ' + temps.C + '&deg; C';
                }
                if (sub === 'cpu') {
                    document.querySelector('#cpu span').innerHTML = json.cpu + '%';
                }
                if (sub === 'memory') {
                    var mem = json.memory;
                    document.querySelector('#mem span').innerHTML = mem.used + ' of ' + mem.total + ' used';
                }
                if (sub === 'running') {
                    [].slice.call(document.querySelectorAll('#actions li.on')).forEach(function(el) {
                        el.className = '';
                    });
                    var cmd = json[sub].command;
                    switch (cmd) {
                        case 'on':
                            document.getElementById('lights_on').className = 'on';
                            break;
                        case 'show':
                            document.getElementById('show_on').className = 'on';
                            break;
                        default:
                            var el = document.getElementById(cmd);
                            if (el) {
                                el.className = 'on';
                            }
                            break;
                    }
                    document.querySelector('small em').innerHTML = 'Last Action was ' + json[sub].since;
		    var uptime = json[sub].uptime.split('.')[0];
		    document.querySelector('#uptime span').innerHTML = uptime;
                }
            });
            var h1 = document.querySelector('h1');
            var enabled = document.getElementById('enable');
            var a = enabled.querySelector('a');
            var img = a.querySelector('img');
            if (json.disabled) {
                if (h1.className !== 'disabled') {
                    h1.className = 'disabled';
                    a.href = './show/enable';
                    img.setAttribute('src', './play.gif');
                    a.innerHTML = a.innerHTML.replace('Disable', 'Enable')
                    document.title = '(disabled) ' + document.title
                }
            } else {
                if (h1.className !== '') {
                    h1.className = '';
                    a.href = './show/disable';
                    img.setAttribute('src', './stop.gif');
                    a.innerHTML = a.innerHTML.replace('Enable', 'Disable')
                    document.title = document.title.replace('(disabled) ', '');
                }
            }
        }
        fetch('./music.json', function(data) {
            var html = 'No music currently playing..';
            if (data.title && data.artist) {
                html = data.title + ' by ' + data.artist;
            }
            document.querySelector('#playing span').innerHTML = html;
            setTimeout(update, 500);
        });
    });
};

update();

var timer;
var show = function(str) {
    if (timer) {
        clearTimeout(timer);
    }
    var el = document.getElementById('message');
    el.innerHTML = str;
    el.className = '';
    timer = setTimeout(function() {
        el.className = 'hide';
    }, 3000);
};

var showLog = function(url, text) {
	if (url.indexOf('logs/setup') === -1) {
		text = text.split('\n').reverse().join('\n');
	}
	var l = document.getElementById('logs');
	var pre = logs.querySelector('pre');
	pre.innerHTML = text;
	l.style.top = (document.documentElement.scrollTop + 10) + 'px';
	var w = 500;
	if (window.innerWidth < w) {
		w = document.innerWidth - 10;
	}
	l.style.width = w + 'px';
	l.className = '';
};

document.getElementById('actions').addEventListener('click', function(e) {
    if (e.target.tagName === 'A') {
        e.preventDefault();
        e.stopPropagation();
        var run = function() {
            fetch(e.target.href, function(json) {
                if (typeof json === 'string') {
                    showLog(e.target.href, json);
                } else {
                    show(json.command + ' was executed..');
                    update();  
                }
            });
        };
        if (e.target.parentNode.className === 'confirm') {
            if (confirm('Are you sure you want to do this?')) {
                run();
            }
            return;
        }
        run();
    }
});

document.querySelector('#logs h3 a').addEventListener('click', function(e) {
	e.preventDefault();
	e.stopPropagation();
	document.getElementById('logs').className = 'hide';
});

})();
