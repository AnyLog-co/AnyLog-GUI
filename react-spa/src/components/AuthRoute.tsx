import React from 'react';
import { Redirect, Route } from 'react-router';
import { useRecoilState } from 'recoil';

import communicatorState from '../lib/communicatorState';

interface Props {
  component: React.FC;
  path: string;
  exact: boolean;
}

const AuthRoute: React.FC<Props> = ({ component, path, exact }) => {
  console.log('render authroute');
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [state] = useRecoilState(communicatorState);
  return state ? <Route path={path} exact={exact} component={component} /> : <Redirect to="/login" />;
};

export default AuthRoute;
