import { atom } from 'recoil';

import Communicator from '.';
import SerDe from './SerDe';

export type OptionalCommunicator = Communicator | undefined;

const fromLocalStorage = (): OptionalCommunicator => {
  const data = localStorage.getItem('communicator');
  if (data) {
    // eslint-disable-next-line no-console
    console.log('Deserializing communicator state');
    try {
      return SerDe.deserialize(data);
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log(error);
      localStorage.removeItem('communicator');
    }
  }
  return undefined;
};

const state = atom<OptionalCommunicator>({
  key: 'communicator',
  default: fromLocalStorage(), // default value (aka initial value)
});

export default state;
