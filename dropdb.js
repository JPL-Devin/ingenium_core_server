var avacado = require('arangojs');
var db = avacado('http://localhost:8529');
db.useBasicAuth('root', 'somepassword');
db.dropDatabase('ingenium')