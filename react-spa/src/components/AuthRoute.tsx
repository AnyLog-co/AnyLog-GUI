import React from 'react';
import { Redirect, Route } from 'react-router';
import { useRecoilState } from 'recoil';

import communicatorState from '../lib/communicatorState';

interface Props {
  children: React.ReactNode;
  path: string;
  exact: boolean;
}

const AuthRoute: React.FC<Props> = ({ path, exact, children }: Props) => {
  const [communicator] = useRecoilState(communicatorState);

  return (
    <Route
      path={path}
      exact={exact}
      render={({ location }) =>
        communicator ? (
          children
        ) : (
          <Redirect
            to={{
              pathname: '/login',
              state: { from: location },
            }}
          />
        )
      }
    />
  );
};

export default AuthRoute;
