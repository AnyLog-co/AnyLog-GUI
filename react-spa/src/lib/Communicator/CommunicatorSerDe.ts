import Communicator from '.';
import ProxyCommunicator from './ProxyCommunicator';
import WebCommunicator from './WebCommunicator';

import isDev from '../isDev';

const version = '1.0';
const watermark = '3c0b2b839f87f169ecbacc6a4a76c0c1864abad2f66aef6a67ee4314a024cf9f';

/**
 *
 * @description Serializer/deserializer for Communicator
 */
class CommunicatorSerDe {
  static serialize(communicator: Communicator): string {
    const data = { version, watermark };
    communicator.dehydrate(data);
    return JSON.stringify(data);
  }

  static deserialize(ser: string): Communicator {
    let data;
    try {
      data = JSON.parse(ser);
    } catch (error) {
      const err = new Error(`Invalid input: Parse failed\n${error.message}`);
      throw err;
    }

    if (data.watermark !== watermark) throw new Error('Invalid input: Unrecognized watermark');
    if (data.version !== version) throw new Error('Invalid input: Unsupported version');

    switch (data.type) {
      case 'WebCommunicator': {
        return isDev
          ? new ProxyCommunicator(data.username, data.password, data.url)
          : new WebCommunicator(data.username, data.password, data.url);
      }
      default: {
        throw new Error('Unable to deserialize Communicator: Unknown type');
      }
    }
  }
}

export default CommunicatorSerDe;
