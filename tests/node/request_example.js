var request = require('request');

var options = {
  'url': 'http://localhost33:8010/api/v4/health2',
  'json': true
};

request.get(options, function(error, response, body) {
  if (error) {
    console.log('error:', JSON.stringify(error, 0, 2));
    console.log('response:', response);
    console.log('body:', body);
  } else {
    console.log('response.statusCode:', response.statusCode);
    console.log('response:', JSON.stringify(response, 0, 2));
    console.log('body:', JSON.stringify(body, 0, 2));
  }
})


