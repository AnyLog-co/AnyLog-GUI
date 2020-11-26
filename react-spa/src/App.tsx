import React, { Suspense } from 'react';

import LoginPage from './pages/LoginPage';
import Spinner from './components/Spinner';
import Language from './components/Language';
// import HomePage from './pages/HomePage';
import './App.css';

function App() {
  return (
    <div className="App">
      <Language />
      <LoginPage />
    </div>
  );
}

// i18n translations might still be loaded by the http backend
const suspense = () => (
  <Suspense fallback={<Spinner />}>
    <App />
  </Suspense>
);

export default suspense;

/*
  <Provider store={store}>
    <Router>
      <NavBar />
      <div className="container">
        <Switch>
          <AuthRoute path="/home" render={HomePage} type="private" />
          <AuthRoute path="/login" type="guest">
            <LoginPage />
          </AuthRoute>
          <AuthRoute path="/my-account" type="private">
            <MyAccount />
          </AuthRoute>
          <Route path="/" render={IndexPage} />
        </Switch>
      </div>
    </Router>
  </Provider>;

  */
