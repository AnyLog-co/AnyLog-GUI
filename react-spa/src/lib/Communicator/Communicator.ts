export interface Node {
  type: 'query' | 'operator' | 'unknown';
  cluster: string;
  name: string;
}

// [{ 'operator': { 'cluster': '496ba074887a7c5c48301d970e9d9b10', 'h4stname': 'localhost', 'name': 'operator1', 'company': 'anylog', 'ip': '172.105.117.98', 'local ip': '172.105.117.98', 'port': '2148', 'rest port': '2149', 'db type': 'psql', 'loc': '1.2929, 103.8547', 'id': '642654015164360928a0e347961b6174', 'date': '2020-12-20T22:20:03.602061Z', 'member': 10 } }]

/**
 * @description Abstract class that interacts with backend API and keeps track of the logged-in
 * user
 */
abstract class Communicator {
  #username: string;

  constructor(username: string) {
    this.#username = username;
  }

  dehydrate(data: Record<string, unknown>): void {
    // eslint-disable-next-line no-param-reassign
    data.username = this.username;
  }

  get username(): string {
    return this.#username;
  }

  abstract logout(): void;

  abstract login(): boolean;

  abstract nodes(company: string): Promise<Node[]>;
}

export default Communicator;
