import React, { Suspense } from 'react';
import ReactDOM from 'react-dom';
import 'typeface-roboto';

import './index.css';
import './i18n';
import App from './App';
import reportWebVitals from './reportWebVitals';
import Store from './lib/Store';
import Spinner from './components/Spinner';

ReactDOM.render(
  <React.StrictMode>
    {
      // i18n translations might be loaded by the http backend
    }
    <Suspense fallback={<Spinner />}>
      <App store={new Store()} />
    </Suspense>
  </React.StrictMode>,
  document.getElementById('root'),
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
