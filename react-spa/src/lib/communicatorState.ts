import { atom } from 'recoil';

import Communicator from './Communicator';

export type OptionalCommunicator = Communicator | undefined;

const communicatorState = atom<OptionalCommunicator>({
  key: 'communicator',
  default: undefined, // default value (aka initial value)
});

export default communicatorState;
