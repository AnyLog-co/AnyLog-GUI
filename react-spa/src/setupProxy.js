const request = require('request');

module.exports = (app) =>
  app.get('/forward', (req, res) => {
    const { headers } = req;
    const uri = headers['x-forward'];
    delete headers['x-forward'];
    delete headers.host; // Needed to work with https
    request({
      uri,
      headers,
    })
      .on('error', (error) => res.status(503).send(error.message))
      .pipe(res);
  });
