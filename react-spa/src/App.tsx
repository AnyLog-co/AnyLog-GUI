import React, { Suspense } from 'react';

import { Route, BrowserRouter as Router, Switch } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import HomePage from './pages/HomePage';
import NoMatch from './pages/NoMatch';
import Spinner from './components/Spinner';
import TopBar from './components/TopBar';
import './App.css';

const App: React.FC = () => {
  return (
    <Router>
      <TopBar />
      <Switch>
        <Route exact path="/login">
          <LoginPage />
        </Route>
        <Route exact path="/">
          <HomePage />
        </Route>
        <Route>
          <NoMatch />
        </Route>
      </Switch>
    </Router>
  );
};

// i18n translations might be loaded by the http backend
const suspense: React.FC = () => (
  <Suspense fallback={<Spinner />}>
    <App />
  </Suspense>
);

export default suspense;

/*
          <AuthRoute path="/home" render={HomePage} type="private" />
          <AuthRoute path="/login" type="guest">
            <LoginPage />
          </AuthRoute>
          <AuthRoute path="/my-account" type="private">
            <MyAccount />
          </AuthRoute>
          <Route path="/" render={IndexPage} />

  */
