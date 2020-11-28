import React, { Suspense } from "react";

import LoginPage from "./pages/LoginPage";
import Spinner from "./components/Spinner";
import TopBar from "./components/TopBar";
import {Router, Switch} from 'react-router';
// import HomePage from './pages/HomePage';
import "./App.css";

const App = (): React.FC => {
  <Fade>
    <Switch>
      <Route exact path="/">
        <Home />
      </Route>
      <Route path="/about">
        <About />
      </Route>
      <Route path="/:user">
        <User />
      </Route>
      <Route>
        <NoMatch />
      </Route>
    </Switch>
  </Fade>

    <div className="App">
      <TopBar />
      <LoginPage />
    </div>
  );
};

// i18n translations might be loaded by the http backend
const suspense: React.FC = () => (
  <Suspense fallback={<Spinner />}>
    <App />
  </Suspense>
);

export default suspense;

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
