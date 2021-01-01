/* eslint-disable no-param-reassign */
import Communicator, { Node, NodeType } from '.';

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
    if (response.status !== 200) throw new Error(`Error ${response.status.toString()}`);
    const result = JSON.parse((await response.text()).replace(/'/g, '"'));
    if (!Array.isArray(result)) throw new Error('Return value is not an array');
    return result;
  }

  private async nodesWithType(type: NodeType): Promise<Node[]> {
    const data = await this.getArray({
      type: 'info',
      details: `blockchain get ${type}`,
    });

    return data.reduce<Node[]>((newData, item) => {
      const { company, cluster, name } = item[type];
      newData.push({ type, company, cluster, name });
      return newData;
    }, []);
  }

  async nodes(): Promise<Node[]> {
    const promises = [NodeType.operator, NodeType.publisher, NodeType.query].map((type) => this.nodesWithType(type)); // :Promise<Node[]>[] =

    const allData: Node[] = [];

    // eslint-disable-next-line no-plusplus
    for (let i = 0; i < promises.length; ++i) {
      // eslint-disable-next-line no-await-in-loop
      allData.push(...(await promises[i]));
    }
    return allData;
  }
}

export default WebCommunicator;
