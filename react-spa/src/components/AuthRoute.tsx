import React from 'react';
import {Redirect, Route} from 'react-router';

const AuthRoute = props => {
  const {isAuthUser, type} = props;
  if (type === 'guest' && isAuthUser) return <Redirect to="/home" />;
  if (type === 'private' && !isAuthUser) return <Redirect to="/" />;

  return <Route {...props} />;
};
