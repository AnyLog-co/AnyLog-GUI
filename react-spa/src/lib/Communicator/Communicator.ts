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

  abstract nodeStatus(): Promise<Record<string, unknown>>;
}

export default Communicator;
