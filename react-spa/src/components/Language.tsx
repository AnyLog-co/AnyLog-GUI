/* eslint-disable react/button-has-type */
import React from 'react';
import { useTranslation } from 'react-i18next';

const Language: React.FC = () => {
  const { t, i18n } = useTranslation();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  return (
    <>
      {t('App.select-language')}
      <button onClick={() => changeLanguage('en_us')}>us</button>
      <button onClick={() => changeLanguage('de')}>de</button>
    </>
  );
};

export default Language;
