import WebCommunicator from './WebCommunicator';

/**
 * @description For development ohnly. Puts the real host name in the host header and sends the request to the proxy
 * running at http://localhost:3000
 */
class ProxyCommunicator extends WebCommunicator {
  // eslint-disable-next-line class-methods-use-this
  alterRequest(/* request: any */): void {
    // TODO: change to Axios type
  }

  dehydrate(data: Record<string, unknown>): void {
    // eslint-disable-next-line no-param-reassign
    if (!data.type) data.type = 'ProxyCommunicator';
    super.dehydrate(data);
  }
}

export default ProxyCommunicator;
