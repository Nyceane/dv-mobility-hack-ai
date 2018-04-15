var express = require('express');
var path = require('path');
var app = express();
var port = process.env.PORT || 8080;
var fs = require('fs');
var data = require('./data/data.json').data;

app.set('view engine', 'ejs');
app.use(express.static( "public"));
app.use(express.static(path.join(__dirname, '/views')));

app.get('/', function(req, res) {
	res.render('search', {'data' : null});
});

app.get('/search', function(req, res) {
	res.render('search', {'data' : null});
});

app.get('/results', function(req, res) {
	res.render('results', {'data' : data});
});

app.get('/details0', function(req, res) {
	res.render('details', {'data' : data[0]});
});

app.get('/details1', function(req, res) {
	res.render('details', {'data' : data[1]});
});

app.get('/details2', function(req, res) {
	res.render('details', {'data' : data[2]});
});

app.get('/details3', function(req, res) {
	res.render('details', {'data' : data[3]});
});

app.get('/details4', function(req, res) {
	res.render('details', {'data' : data[4]});
});

app.get('/details5', function(req, res) {
	res.render('details', {'data' : data[5]});
});

app.get('/details6', function(req, res) {
	res.render('details', {'data' : data[6]});
});

app.get('/details7', function(req, res) {
	res.render('details', {'data' : data[7]});
});

app.get('/details8', function(req, res) {
	res.render('details', {'data' : data[8]});
});

app.get('/video0', function(req, res) {
  getVideo(req, res, 'data/output0.mp4')
});

app.get('/video1', function(req, res) {
  getVideo(req, res, 'data/output1.mp4')
});

app.get('/video2', function(req, res) {
  getVideo(req, res, 'data/output2.mp4')
});

app.get('/video3', function(req, res) {
  getVideo(req, res, 'data/output3.mp4')
});

app.get('/video4', function(req, res) {
  getVideo(req, res, 'data/output4.mp4')
});

app.get('/video5', function(req, res) {
  getVideo(req, res, 'data/output5.mp4')
});

app.get('/video6', function(req, res) {
  getVideo(req, res, 'data/output6.mp4')
});

app.get('/video7', function(req, res) {
  getVideo(req, res, 'data/output7.mp4')
});

app.get('/video8', function(req, res) {
  getVideo(req, res, 'data/output8.mp4')
});
function getVideo(req, res, path) {
  var stat = fs.statSync(path)
  var fileSize = stat.size
  var range = req.headers.range
  if (range) {
    var parts = range.replace(/bytes=/, "").split("-")
    var start = parseInt(parts[0], 10)
    var end = parts[1] ? parseInt(parts[1], 10) : fileSize-1;
    var chunksize = (end-start)+1
    var file = fs.createReadStream(path, {start, end})
    var head = {
      'Content-Range': `bytes ${start}-${end}/${fileSize}`,
      'Accept-Ranges': 'bytes',
      'Content-Length': chunksize,
      'Content-Type': 'video/mp4',
    }
    res.writeHead(206, head);
    file.pipe(res);
  } else {
    var head = {
      'Content-Length': fileSize,
      'Content-Type': 'video/mp4',
    }
    res.writeHead(200, head)
    fs.createReadStream(path).pipe(res)
  }
}

app.listen(port);
console.log("Listening to port", port);