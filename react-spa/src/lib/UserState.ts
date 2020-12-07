import Communicator from './Communicator';

class UserState {
  communicator?: Communicator;

  get authenticated(): boolean {
    return !!this.communicator;
  }

  get username(): string {
    return this.communicator ? this.communicator.username : '';
  }
}

export default UserState;
