/* eslint-disable no-param-reassign */
import Communicator, { Node } from './Communicator';

class WebCommunicator extends Communicator {
  #url: string;

  #password: string;

  constructor(username: string, password: string, url: string) {
    super(username);
    this.#password = password;
    this.#url = url;
  }

  dehydrate(data: Record<string, unknown>): void {
    if (!data.type) data.type = 'WebCommunicator';
    data.password = this.#password;
    data.url = this.#url;
    super.dehydrate(data);
  }

  get url(): string {
    return this.#url;
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  forward(headers: Record<string, string>): string {
    return this.#url;
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
  private async getArray(headers: Record<string, string>): Promise<Record<string, any>[]> {
    const url = this.forward(headers);
    const response = await fetch(url, { headers });
    if (response.status !== 200) throw new Error(response.status.toString());
    return JSON.parse((await response.text()).replace(/'/g, '"'));
  }

  async nodes(company: string): Promise<Node[]> {
    const data = await this.getArray({
      type: 'info',
      details: `blockchain get operator where company = ${company}`,
    });

    if (!data) return [];

    const newData: Node[] = data.map((item) => {
      const first = Object.keys(item)[0];
      const type = first === ('operator' || 'query') ? first : 'unknown';

      let cluster: string;
      let name: string;

      if (type === 'unknown') {
        cluster = '';
        name = '';
      } else {
        ({ cluster, name } = item[type]);
      }

      return { type, cluster, name };
    });

    return newData;
  }
}

export default WebCommunicator;
