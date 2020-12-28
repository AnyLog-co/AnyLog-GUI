import React from 'react';
import { RecoilRoot } from 'recoil';

import ErrorHandler from './ErrorHandler';
import Routes from './Routes';
import Header from './Header';

const App: React.FC = () => (
  <ErrorHandler>
    <RecoilRoot>
      <Header />
      <Routes />
    </RecoilRoot>
  </ErrorHandler>
);

export default App;
