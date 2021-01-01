import React from 'react';
import { RecoilRoot } from 'recoil';

import ErrorHandler from './ErrorHandler';
import Root from './Root';

const App: React.FC = () => (
  <RecoilRoot>
    <ErrorHandler>
      <Root />
    </ErrorHandler>
  </RecoilRoot>
);

export default App;
