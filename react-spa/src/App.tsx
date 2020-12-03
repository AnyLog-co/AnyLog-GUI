import React from 'react';
import { Route, Switch, BrowserRouter } from 'react-router-dom';

import './App.css';
import Login from './views/Login';
import Home from './views/Home';
import NotFound from './views/NotFound';
import UserContext from './components/UserContext';
import AuthRoute from './components/AuthRoute';
import Header from './views/Header';

const App: React.FC = () => (
  <BrowserRouter>
    <UserContext.Provider>
      <Header />
      <Switch>
        <AuthRoute exact path="/" component={Home} />
        <Route exact path="/login">
          <Login />
        </Route>
        <Route exact path="/">
          <NotFound />
        </Route>
      </Switch>
    </UserContext.Provider>
  </BrowserRouter>
);

export default App;
