'use strict';

// Not needed
// See https://create-react-app.dev/docs/proxying-api-requests-in-development/

const request = require('request');

/**
 * @param {Object} app
 */
const handler = (app) =>
  app.get('/api', (req, res) => {
    // make request to IEX API and forward response
    delete req.headers.host;
    const uri = req.headers.location;
    delete req.headers.location;
    request({
      uri,
      headers: req.headers,
    }).pipe(res);
  });

module.exports = handler;
