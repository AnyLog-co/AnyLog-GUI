// See https://create-react-app.dev/docs/proxying-api-requests-in-development/

import { createProxyMiddleware } from 'http-proxy-middleware';

/**
 * @param {Object} req See https://expressjs.com/en/5x/api.html#req
 */
const router = () =>
  // const x = `${req.protocol}://${req.host}:5000${req.url}`;
  // console.log(x);
  'https://api.github.com/repos/tannerlinsley/react-query';
/**
 * @param {Object} app See https://expressjs.com/en/5x/api.html#req
 */
const handler = (app) =>
  app.use(
    '/api',
    createProxyMiddleware({
      // I don't know why this is used but it seems to override what router returns
      target: 'http://localhost', // It has to be nonblank
      router,
      changeOrigin: true, // What does this do?
    }),
  );

export default handler;
