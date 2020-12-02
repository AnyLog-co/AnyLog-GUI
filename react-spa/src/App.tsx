import React from 'react';
import { Route, Switch, BrowserRouter } from 'react-router-dom';
import { observer } from 'mobx-react-lite';

import './App.css';
import Login from './views/Login';
import Home from './views/Home';
import NotFound from './views/NotFound';

import AuthRoute from './components/AuthRoute';
import TopBar from './components/TopBar';
import { UserStoreProvider } from './components/UserStore';

const App: React.FC = observer(() => (
  <UserStoreProvider>
    <TopBar />
    <BrowserRouter>
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
  </UserStoreProvider>
));

export default App;
