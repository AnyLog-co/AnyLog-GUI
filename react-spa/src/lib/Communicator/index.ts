/**
 * @description Abstract class that interacts with backend API
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
}

export default Communicator;
