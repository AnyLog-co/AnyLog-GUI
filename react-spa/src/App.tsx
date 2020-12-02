import React from 'react';
import { Route, Switch, BrowserRouter } from 'react-router-dom';

import './App.css';
// import Login from './views/Login';
import Home from './views/Home';
import NotFound from './views/NotFound';
import { UserContextProvider } from './components/UserContext';
// import AuthRoute from './components/AuthRoute';
import TopBar from './views/TopBar';

const App: React.FC = () => (
  <UserContextProvider>
    <BrowserRouter>
      <TopBar />
      <Switch>
        <Route exact path="/a">
          <Home />
        </Route>
        <Route exact path="/">
          <NotFound />
        </Route>
      </Switch>
    </BrowserRouter>
  </UserContextProvider>
);

export default App;
