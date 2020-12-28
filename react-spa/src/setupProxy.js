const request = require('request');

module.exports = (app) =>
  app.get('/forward', (req, res) => {
    const { headers } = req;
    const uri = headers['x-forward'];
    delete headers['x-forward'];
    delete headers.host; // Needed to work with https
    let req2;
    try {
      req2 = request({
        uri,
        headers,
      });
    } catch (error) {
      res.status(400).send(error.message);
    }
    if (req2) req2.on('error', (error) => res.status(503).send(error.message)).pipe(res);
  });
