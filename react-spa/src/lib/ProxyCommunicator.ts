import WebCommunicator from './WebCommunicator';

/**
 * @description For development ohnly. Puts the real host name in the host header and sends the request to the proxy
 * running at http://localhost:3000
 */
class ProxyCommunicator extends WebCommunicator {
  // eslint-disable-next-line class-methods-use-this
  alterRequest(/* request: any */): void {
    // @todo change to Axios type
  }

  // eslint-disable-next-line no-useless-constructor
  constructor(username: string, url: string) {
    super(username, url);
  }
}

export default ProxyCommunicator;
