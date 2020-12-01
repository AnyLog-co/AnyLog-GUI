import React, { useContext } from 'react';
import { Redirect, Route } from 'react-router';

import Store from '../lib/Store';

interface Props {
  component: React.FC;
  path: string;
  exact: boolean;
}

const AuthRoute: React.FC<Props> = ({ component, path, exact }) => {
  const store = useContext(Store);
  return store.authenticated ? <Route path={path} exact={exact} component={component} /> : <Redirect to="/login" />;
};

export default AuthRoute;
