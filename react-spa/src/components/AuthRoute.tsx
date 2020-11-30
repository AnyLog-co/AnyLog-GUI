import React, { useContext } from 'react';
import { Redirect, Route } from 'react-router';

import Store from '../lib/Store';

interface Props {
  access: 'guest' | 'private';
}

// This will be changed to use state
// eslint-disable-next-line react/prop-types
const AuthRoute: React.FC<Props> = ({ access, children, ...props }) => {
  const store = useContext(Store);
  const isAuthUser = store.authenticated;
  if (access === 'guest' && isAuthUser) return <Redirect to="/home" />;
  if (access === 'private' && !isAuthUser) return <Redirect to="/" />;

  // eslint-disable-next-line react/jsx-props-no-spreading
  return <Route {...props}>{children}</Route>;
};

export default AuthRoute;
