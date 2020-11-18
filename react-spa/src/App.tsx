/* eslint-disable react/button-has-type */
/* eslint-disable react/jsx-no-comment-textnodes */
import React, { Suspense } from 'react';
import { useTranslation } from 'react-i18next';

import Login from './Login';
import Spinner from './Spinner';
import './App.css';

function App() {
  const { t, i18n } = useTranslation();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  return (
    <div className="App">
      <div>
        {t('App.select-language')}
        <button onClick={() => changeLanguage('en')}>en</button>
        <button onClick={() => changeLanguage('de')}>de</button>
      </div>
      <header className="App-header">
        <Login />
      </header>
    </div>
  );
}

// i18n translations might still be loaded by the http backend
const suspense = () => (
  <Suspense fallback={<Spinner />}>
    <App />
  </Suspense>
);

export default suspense;
