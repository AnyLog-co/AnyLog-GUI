import React from 'react';
import { Route, Switch, BrowserRouter } from 'react-router-dom';

import Login from './Login';
import Home from './Home';
import QueryExample from './QueryExample';
import Nodes from './network/Nodes';
import AuthRoute from './AuthRoute';
import NotFound from './NotFound';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Switch>
        <Route exact path="/login">
          <Login />
        </Route>
        <Route exact path="/queryExample">
          <QueryExample />
        </Route>
        <AuthRoute exact path="/">
          <Home />
        </AuthRoute>
        <AuthRoute exact path="/network/nodes">
          <Nodes />
        </AuthRoute>
        <Route>
          <NotFound />
        </Route>
      </Switch>
    </BrowserRouter>
  );
};

export default App;
