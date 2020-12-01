import React from 'react';
import { Redirect, Route } from 'react-router';
import { observer } from 'mobx-react-lite';

import Store from '../lib/Store';

interface Props {
  store: Store;
  component: React.FC;
  path: string;
  exact: boolean;
}

const AuthRoute: React.FC<Props> = observer(({ store, component, path, exact }: Props) => {
  return store.authenticated ? <Route path={path} exact={exact} component={component} /> : <Redirect to="/login" />;
});

export default AuthRoute;
