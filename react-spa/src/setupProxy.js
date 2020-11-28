// See https://create-react-app.dev/docs/proxying-api-requests-in-development/
import { createProxyMiddleware } from "http-proxy-middleware";

// https://expressjs.com/en/5x/api.html#req
const router = (req) => {
  return req.protocol + req.host;
};

export default (app) => app.use(
  "/",
  createProxyMiddleware({
    router,
    // changeOrigin: true,
  }));
};
