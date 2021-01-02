import { QueryClient } from 'react-query';

export enum NodeType {
  query = 'query',
  publisher = 'publisher',
  operator = 'operator',
}

export interface Node {
  type: NodeType;
  company: string;
  cluster?: string;
  name: string;
  hostname: string;
  ip: string;
  'local ip': string;
  port: number;
}

/**
 * @description Abstract class that interacts with backend API and keeps track of the logged-in
 * user
 */
abstract class Communicator {
  #username: string;

  #queryClient: QueryClient = new QueryClient();

  constructor(username: string) {
    this.#username = username;
  }

  dehydrate(data: Record<string, unknown>): void {
    // eslint-disable-next-line no-param-reassign
    data.username = this.username;
  }

  get queryClient(): QueryClient {
    return this.#queryClient;
  }

  get username(): string {
    return this.#username;
  }

  abstract logout(): void;

  abstract login(): boolean;

  abstract nodes(): Promise<Node[]>;
}

export default Communicator;
