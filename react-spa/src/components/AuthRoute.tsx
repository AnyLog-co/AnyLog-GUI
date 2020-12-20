import React from 'react';
import { Redirect, Route } from 'react-router';
import { useRecoilState } from 'recoil';

import communicatorState, { OptionalCommunicator } from '../lib/communicatorState';
import CommunicatorSerDe from '../lib/Communicator/CommunicatorSerDe';

interface Props {
  component: React.FC;
  path: string;
  exact: boolean;
}

const AuthRoute: React.FC<Props> = ({ component, path, exact }) => {
  // eslint-disable-next-line prettier/prettier, prefer-const
  let [communicator, setCommunicator] = useRecoilState<OptionalCommunicator>(communicatorState);

  if (!communicator) {
    // Load from local state
    const data = localStorage.getItem('communicator');
    if (data) {
      try {
        communicator = CommunicatorSerDe.deserialize(data);
        setImmediate(() => setCommunicator(communicator));
      } catch (error) {
        // eslint-disable-next-line no-console
        console.log(error);
        localStorage.removeItem('communicator');
      }
    }
  }

  return communicator ? <Route path={path} exact={exact} component={component} /> : <Redirect to="/login" />;
};

export default AuthRoute;
