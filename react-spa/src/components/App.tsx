import React from 'react';
import { RecoilRoot } from 'recoil';
import CssBaseline from '@material-ui/core/CssBaseline';

import ErrorHandler from './ErrorHandler';
import Root from './Root';

const App: React.FC = () => (
  <RecoilRoot>
    <CssBaseline />
    <ErrorHandler>
      <Root />
    </ErrorHandler>
  </RecoilRoot>
);

export default App;
