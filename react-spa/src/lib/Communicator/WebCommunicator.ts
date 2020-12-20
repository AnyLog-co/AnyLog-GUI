/* eslint-disable no-param-reassign */
import Communicator from '.';

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

  // TODO change to Axios type
  // eslint-disable-next-line class-methods-use-this
  alterRequest(/* request: any */): void {
    //
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars, class-methods-use-this
  login(): boolean {
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
