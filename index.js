const express = require('express');
const cors = require('cors');
const path = require('path');
const dotenv = require('dotenv');
dotenv.config();
const app = express();
const port = process.env.PORT || 4180;

app.use(express.static(path.join(__dirname, 'public')))
   .use(cors());


app.get('/', function (req, res) {
  res.sendFile(path.join(__dirname + '/public/index.html'));
});

app.listen(port, function () {
  console.log(`Listening on port ${port}!`);
});
