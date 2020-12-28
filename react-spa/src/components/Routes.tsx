import React from 'react';
import { Route, Switch, BrowserRouter } from 'react-router-dom';
import { useRecoilState } from 'recoil';
import { QueryClientProvider, QueryClient } from 'react-query';
import { ReactQueryDevtools } from 'react-query/devtools';

import Login from '../views/Login';
import Home from '../views/Home';
import QueryExample from './QueryExample';
import Nodes from './network/Nodes';
import AuthRoute from './AuthRoute';
import communicatorState from '../lib/communicatorState';
import NotFound from '../views/NotFound';

const App: React.FC = () => {
  const [communicator] = useRecoilState(communicatorState);
  const queryClient = communicator ? communicator.queryClient : new QueryClient();

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Switch>
          <Route exact path="/login">
            <Login />
          </Route>
          <Route exact path="/queryExample">
            <QueryExample />
          </Route>
          <AuthRoute exact path="/">
            <Home />
          </AuthRoute>
          <AuthRoute exact path="/network/nodes">
            <Nodes />
          </AuthRoute>
          <Route>
            <NotFound />
          </Route>
        </Switch>
      </BrowserRouter>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
};

export default App;
