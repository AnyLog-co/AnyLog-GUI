/* eslint-disable no-param-reassign */
import WebCommunicator from './WebCommunicator';

/**
 * @description For development ohnly. Puts the real host name in the host header and sends the request to the proxy
 * running at http://localhost:3000
 */
class ProxyCommunicator extends WebCommunicator {
  // eslint-disable-next-line class-methods-use-this
  protected forward(headers: Record<string, string>, url: string): string {
    headers['X-Forward'] = url || this.url;
    return '/forward';
  }
}

export default ProxyCommunicator;
