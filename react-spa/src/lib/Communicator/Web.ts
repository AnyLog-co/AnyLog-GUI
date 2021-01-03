/* eslint-disable no-await-in-loop */
/* eslint-disable no-plusplus */
/* eslint-disable no-param-reassign */
import { JsonDecoder } from 'ts.data.json';

import Communicator, { Node, NodeType, NodeStatus, Location } from '.';

interface NodeKeys {
  company: string;
  cluster?: string;
  name: string;
  hostname: string;
  ip: string;
  'local ip': string;
  port: string;
  'rest port': string;
  loc: string;
}

const nodeKeysDecoder = JsonDecoder.object<NodeKeys>(
  {
    company: JsonDecoder.string,
    cluster: JsonDecoder.optional(JsonDecoder.string),
    name: JsonDecoder.string,
    hostname: JsonDecoder.string,
    ip: JsonDecoder.string,
    'local ip': JsonDecoder.string,
    port: JsonDecoder.string,
    'rest port': JsonDecoder.string,
    loc: JsonDecoder.string,
  },
  'NodeKeys',
);

class Web extends Communicator {
  #url: string;

  #password: string;

  constructor(username: string, password: string, url: string) {
    super(username);
    this.#password = password;
    this.#url = url;
  }

  dehydrate(data: Record<string, unknown>): void {
    if (!data.type) data.type = 'Web';
    data.password = this.#password;
    data.url = this.#url;
    super.dehydrate(data);
  }

  get url(): string {
    return this.#url;
  }

  /**
   * @description If invoked on the ProxyCommunicator subclass, headers and the URL are altered to use the CORS proxy
   * @return The url to fetch
   */
  // eslint-disable-next-line @typescript-eslint/no-unused-vars, class-methods-use-this
  protected forward(headers: Record<string, string>, url: string): string {
    return url;
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  private prepare(headers: Record<string, string>, url?: string): string {
    headers.pragma = 'no-cache';
    headers['cache-control'] = 'no-store';
    url = url || this.#url;
    return this.forward(headers, url);
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars, class-methods-use-this
  login(): boolean {
    return true;
  }

  // eslint-disable-next-line class-methods-use-this
  logout(): void {
    // TODO
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private async getObject(headers: Record<string, string>, url?: string): Promise<Record<string, any>> {
    url = this.prepare(headers, url);
    // Because the url and method are always the same (only the headers change), XmlHttp caches the wrong response to
    // different requests
    const response = await fetch(url, { headers });
    if (response.status !== 200) throw new Error(`Error ${response.status.toString()}`);
    const result = JSON.parse((await response.text()).replace(/'/g, '"'));
    if (typeof result !== 'object' || Array.isArray(result)) throw new Error('Return value is not an object');
    return result;
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private async getArray(headers: Record<string, string>, url?: string): Promise<Record<string, any>[]> {
    url = this.prepare(headers, url);
    // Because the url and method are always the same (only the headers change), XmlHttp caches the wrong response to
    // different requests
    headers.pragma = 'no-cache';
    headers['cache-control'] = 'no-store';
    const response = await fetch(url, { headers });
    if (response.status !== 200) throw new Error(`Error ${response.status.toString()}`);
    const result = JSON.parse((await response.text()).replace(/'/g, '"'));
    if (!Array.isArray(result)) throw new Error('Return value is not an array');
    return result;
  }

  /**
   * @description Returns an array of nodes for a specified type
   */
  private async nodesWithType(type: NodeType): Promise<Node[]> {
    const data = await this.getArray({
      type: 'info',
      details: `blockchain get ${type}`,
    });

    const results: Node[] = [];

    for (let i = 0; i < data.length; ++i) {
      let item = data[i];
      item = item[type];
      if (!item) throw new Error(`Nodes item is missing expected type '${type}'`);
      const nodeKeys = await nodeKeysDecoder.decodePromise(item);
      let location: Location;
      {
        const components = nodeKeys.loc.split(',');
        location = { lat: Number(components[0]), long: Number(components[1]) };
      }
      // Get the status
      let status: NodeStatus = NodeStatus.unknown;
      try {
        // TODO: http vs https
        const url = `http://${nodeKeys.ip}:${nodeKeys['rest port']}`;
        const response = await this.getObject(
          {
            type: 'info',
            details: 'get status',
          },
          url,
        );
        const parts = response.Status.split(' ');
        if (parts.length === 2) {
          if (parts[1] === 'running') status = NodeStatus.running;
        }
      } catch (error) {
        // eslint-disable-next-line no-console
        console.log(error);
      }
      const copy = {
        ...nodeKeys,
        port: Number(nodeKeys.port),
        'rest port': Number(nodeKeys['rest port']),
        location,
        status,
      };
      results.push({ type, ...copy });
    }

    return results;
  }

  async nodes(): Promise<Node[]> {
    const promises = [NodeType.operator, NodeType.publisher, NodeType.query].map((type) => this.nodesWithType(type));

    const allData: Node[] = [];

    for (let i = 0; i < promises.length; ++i) {
      allData.push(...(await promises[i]));
    }
    return allData;
  }
}

export default Web;
