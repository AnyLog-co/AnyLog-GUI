import Communicator from './Communicator';

class UserState {
  communicator?: Communicator;

  get authenticated(): boolean {
    return !!this.communicator;
  }

  // eslint-disable-next-line class-methods-use-this
  logout(): void {
    //
  }
}

export default UserState;
