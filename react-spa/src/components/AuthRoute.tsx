import React from 'react';
import { Redirect, Route } from 'react-router';

const AuthRoute = (props: any) => {
  const { isAuthUser, type } = props;
  if (type === 'guest' && isAuthUser) return <Redirect to="/home" />;
  if (type === 'private' && !isAuthUser) return <Redirect to="/" />;

  // eslint-disable-next-line react/jsx-props-no-spreading
  return <Route {...props} />;
};

export default AuthRoute;
