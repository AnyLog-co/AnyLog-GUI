import React from 'react';
import { Route, Switch, BrowserRouter } from 'react-router-dom';

// Components
import AuthRoute from './AuthRoute';
import NotFound from './NotFound';

// Views
import Login from '../views/Login';
import Nodes from '../views/Nodes';
import Home from '../views/Home';
import Logout from '../views/Logout';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Switch>
        <Route exact path="/login">
          <Login />
        </Route>
        <Route exact path="/logout">
          <Logout />
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
