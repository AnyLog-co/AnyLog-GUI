import { QueryClient } from 'react-query';

export interface Node {
  type: 'query' | 'operator' | 'unknown';
  cluster: string;
  name: string;
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

  abstract nodes(company: string): Promise<Node[]>;
}

export default Communicator;
