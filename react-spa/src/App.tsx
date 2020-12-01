import React, { Suspense } from 'react';

import { Route, BrowserRouter as Router, Redirect, Switch } from 'react-router-dom';

import AuthRoute from './components/AuthRoute';
import Login from './views/Login';
import Home from './views/Home';
import NoMatch from './views/NoMatch';
import Spinner from './components/Spinner';
import TopBar from './components/TopBar';
import './App.css';

const App: React.FC = () => (
  <Router>
    <TopBar />
    <Switch>
      <Redirect from="/" to="/home" exact />
      <AuthRoute exact path="/home" component={Home} />
      <Route exact path="/login">
        <Login />
      </Route>
      <Route>
        <NoMatch />
      </Route>
    </Switch>
  </Router>
);

// i18n translations might be loaded by the http backend
const suspense: React.FC = () => (
  <Suspense fallback={<Spinner />}>
    <App />
  </Suspense>
);

export default suspense;
