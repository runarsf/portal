const express = require('express');
var path = require('path');
const dotenv = require('dotenv');
dotenv.config();
const app = express();
const port = process.env.PORT || 4180;

app.use(express.static(path.join(__dirname, 'public')));


app.get('/', function (req, res) {
  res.sendFile(path.join(__dirname + '/public/index.html'));
});

app.listen(port, function () {
  console.log(`Listening on port ${port}!`);
});