import { atom } from 'recoil';

import Communicator from './Communicator';

const communicatorState = atom<Communicator | undefined>({
  key: 'communicator',
  default: undefined, // default value (aka initial value)
});

export default communicatorState;
