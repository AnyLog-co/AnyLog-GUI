import React from 'react';
import { Redirect, Route } from 'react-router';

import { useUserContext } from './UserContext';

interface Props {
  component: React.FC;
  path: string;
  exact: boolean;
}

const AuthRoute: React.FC<Props> = ({ component, path, exact }) => {
  const store = useUserContext();
  return store.authenticated ? <Route path={path} exact={exact} component={component} /> : <Redirect to="/login" />;
};

export default AuthRoute;
