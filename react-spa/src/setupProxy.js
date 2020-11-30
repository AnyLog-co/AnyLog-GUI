// See https://create-react-app.dev/docs/proxying-api-requests-in-development/

// eslint-disable-next-line @typescript-eslint/no-var-requires
const { createProxyMiddleware } = require('http-proxy-middleware');

/**
 * @param {Object} req See https://expressjs.com/en/5x/api.html#req
 */
const router = (req) => {
  return req.protocol + req.host;
};

/**
 * @param {Object} app See https://expressjs.com/en/5x/api.html#req
 */
const handler = (app) =>
  app.use(
    '/api',
    createProxyMiddleware({
      target: '',
      router,
      changeOrigin: true,
    }),
  );

module.exports = handler;
