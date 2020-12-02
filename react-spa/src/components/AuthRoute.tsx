import React from 'react';
import { Redirect, Route } from 'react-router';

import { UserStoreConsumer, UserStore } from './UserStore';

interface Props {
  store: Store;
  component: React.FC;
  path: string;
  exact: boolean;
}

// @todo store probably doesn't need to be observed
const AuthRoute: React.FC<Props> = ({ component, path, exact }: Props) => {
  return 
  
  store.authenticated ? <Route path={path} exact={exact} component={component} /> : <Redirect to="/login" />;
};

export default AuthRoute;
