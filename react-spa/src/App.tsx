import React from 'react';
import { Route, Redirect, Switch, BrowserRouter } from 'react-router-dom';
import { observer } from 'mobx-react-lite';

import './App.css';
import AuthRoute from './components/AuthRoute';
import Login from './views/Login';
import Home from './views/Home';
import NoMatch from './views/NoMatch';
import TopBar from './components/TopBar';
import Store from './lib/Store';

interface Props {
  store: Store;
}

const App: React.FC<Props> = observer(({ store }: Props) => (
  <>
    <TopBar />
    <BrowserRouter>
      <Switch>
        <Redirect from="/" to="/home" exact />
        <AuthRoute exact path="/home" component={Home} store={store} />
        <Route exact path="/login">
          <Login store={store} />
        </Route>
        <Route>
          <NoMatch />
        </Route>
      </Switch>
    </BrowserRouter>
  </>
));

export default App;
