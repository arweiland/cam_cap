#!/usr/bin/node

// Quick and dirty node.js static web server

var express = require('express');
 
var server = express();
server.use(express.static(__dirname + '/public'));
var port = 8181;
server.listen(port, function() {
    console.log('server listening on port ' + port);
});
