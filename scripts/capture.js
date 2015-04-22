var page = require('webpage').create();
var url = 'https://www.python.org';
var size = {width: 1366, height: 768};
var output = 'python.png';

page.viewportSize = size;
page.open(url, function(){
    page.render('python.png');
    phantom.exit();
});
