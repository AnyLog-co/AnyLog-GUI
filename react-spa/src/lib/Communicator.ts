abstract class Communicator {
  #username: string;

  constructor(username: string) {
    this.#username = username;
  }

  get username(): string {
    return this.#username;
  }

  abstract logout(): void;

  abstract login(password: string): boolean;
}

export default Communicator;
