import React from 'react';
import { Route, Switch, BrowserRouter } from 'react-router-dom';
import { RecoilRoot } from 'recoil';
import { ReactQueryDevtools } from 'react-query/devtools';
import { QueryClientProvider } from 'react-query';

import Login from '../views/Login';
import Home from '../views/Home';
import NotFound from '../views/NotFound';
import QueryExample from './QueryExample';
import Nodes from './anylog/Nodes';
import AuthRoute from './AuthRoute';
import Header from '../views/Header';
import queryClient from '../lib/queryClient';
import ErrorHandler from './ErrorHandler';

const App: React.FC = () => (
  <ErrorHandler>
    <QueryClientProvider client={queryClient}>
      <RecoilRoot>
        <BrowserRouter>
          <Header />
          <Switch>
            <AuthRoute exact path="/queryExample">
              <QueryExample />
            </AuthRoute>
            <AuthRoute exact path="/nodes">
              <Nodes />
            </AuthRoute>
            <AuthRoute exact path="/">
              <Home />
            </AuthRoute>
            <Route exact path="/login">
              <Login />
            </Route>
            <Route>
              <NotFound />
            </Route>
          </Switch>
        </BrowserRouter>
      </RecoilRoot>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </ErrorHandler>
);

export default App;
