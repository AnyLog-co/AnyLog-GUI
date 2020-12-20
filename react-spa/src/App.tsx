import React from 'react';
import { Route, Switch, BrowserRouter } from 'react-router-dom';

import './App.css';
import Login from './views/Login';
import Home from './views/Home';
import NotFound from './views/NotFound';
import AuthRoute from './components/AuthRoute';
import Header from './views/Header';

const App: React.FC = () => (
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
);

export default App;
