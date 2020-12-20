import React from 'react';
import { Route, Switch, BrowserRouter } from 'react-router-dom';
import { RecoilRoot } from 'recoil';

import Login from '../views/Login';
import Home from '../views/Home';
import NotFound from '../views/NotFound';
import AuthRoute from './AuthRoute';
import Header from '../views/Header';

const App: React.FC = () => (
  <RecoilRoot>
    <BrowserRouter>
      <Header />
      <Switch>
        <AuthRoute exact path="/" component={Home} />
        <Route exact path="/login">
          <Login />
        </Route>
        <Route>
          <NotFound />
        </Route>
      </Switch>
    </BrowserRouter>
  </RecoilRoot>
);

export default App;
