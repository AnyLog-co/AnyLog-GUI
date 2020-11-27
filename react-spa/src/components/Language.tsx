/* eslint-disable react/button-has-type */
import React from "react";
import { useTranslation } from "react-i18next";

const Language = () => {
  const { t, i18n } = useTranslation();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  return (
    <div>
      {t("App.select-language")}
      <button onClick={() => changeLanguage("en")}>en</button>
      <button onClick={() => changeLanguage("de")}>de</button>
    </div>
  );
};

export default Language;
