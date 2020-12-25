const request = require('request');

module.exports = (app) =>
  app.get('/external', (req, res) => {
    const { headers } = req;
    const uri = headers['x-forward'];
    delete headers['x-forward'];
    delete headers.host; // Needed to work with https
    request({
      uri,
      headers,
    }).pipe(res);
  });
