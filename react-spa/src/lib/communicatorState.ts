import { atom } from 'recoil';

import Communicator from './Communicator/Communicator';
import CommunicatorSerDe from './Communicator/CommunicatorSerDe';

export type OptionalCommunicator = Communicator | undefined;

const fromLocalStorage = () => {
  console.log('** from local storage');
  const data = localStorage.getItem('communicator');
  if (data) {
    try {
      return CommunicatorSerDe.deserialize(data);
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log(error);
      localStorage.removeItem('communicator');
    }
  }
  return undefined;
};

const communicatorState = atom<OptionalCommunicator>({
  key: 'communicator',
  default: fromLocalStorage(), // default value (aka initial value)
});

export default communicatorState;
