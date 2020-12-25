/* eslint-disable no-param-reassign */
import axios from 'axios';

import Communicator from './Communicator';

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

  // {'type': 'info', 'details': 'blockchain get operator where company = anylog'}
  // [{'operator': {'cluster': '496ba074887a7c5c48301d970e9d9b10', 'h4stname': 'localhost', 'name': 'operator1', 'company': 'anylog', 'ip': '172.105.117.98', 'local ip': '172.105.117.98', 'port': '2148', 'rest port': '2149', 'db type': 'psql', 'loc': '1.2929, 103.8547', 'id': '642654015164360928a0e347961b6174', 'date': '2020-12-20T22:20:03.602061Z', 'member': 10}}]
  // `blockchain get operator where company = ${entity}`;

  // curl --location --request GET 'http://172.105.117.98:2249'    --header 'type: info'  --header 'details: blockchain get operator where company = anylog'
  // [{'operator': {'cluster': '496ba074887a7c5c48301d970e9d9b10', 'hostname': 'localhost', 'name': 'operator1', 'company': 'anylog', 'ip': '172.105.117.98', 'local ip': '172.105.117.98', 'port': '2148', 'rest port': '2149', 'db type': 'psql', 'loc': '1.2929, 103.8547', 'id': '642654015164360928a0e347961b6174', 'date': '2020-12-20T22:20:03.602061Z', 'member': 10}}]

  // eslint-disable-next-line class-methods-use-this, @typescript-eslint/no-unused-vars
  async nodeStatus(): Promise<Record<string, unknown>> {
    const response = await axios.get(this.#url, {
      headers: {
        type: 'info',
        details: 'blockchain get operator where company = anylog',
      },
    });
    return JSON.parse(response.data.replace(/'/g, '"'));
  }
}

export default WebCommunicator;
