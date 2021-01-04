import React from 'react';
import { Redirect } from 'react-router';
import { useRecoilState } from 'recoil';

import communicatorState from '../lib/Communicator/state';

const Logout: React.FC = () => {
  const [communicator, setCommunicator] = useRecoilState(communicatorState);

  if (communicator) {
    // TODO
    localStorage.removeItem('communicator');
    setCommunicator(undefined);
  }
  return <Redirect to="/" />;
};

export default Logout;
