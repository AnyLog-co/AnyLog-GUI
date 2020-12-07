import Communicator from './Communicator';

class WebCommunicator extends Communicator {
  #url: string;

  constructor(username: string, url: string) {
    super(username);
    this.#url = url;
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars, class-methods-use-this
  login(password: string): boolean {
    return true;
  }

  // eslint-disable-next-line class-methods-use-this
  logout(): void {
    //
  }

  // login(username: string, password: string) {
  //   fetch('http://localhost:8088/api/login', {
  //      username: authData.username,
  //  password: authData.password
  // }, {
  //  mode: 'no-cors',
  //  method: 'post',
  //  url: `http://localhost:8088`,
  //  credentials: 'include'
  // })

  //
  //  curl --location --request GET '172.105.117.98:2069' \
  // --header 'type: sql' \
  // --header 'dbms: sample_data' \
  // --header 'details: SELECT * FROM machine_data;'
}

export default WebCommunicator;
