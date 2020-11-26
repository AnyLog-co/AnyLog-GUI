# How this app was created

## Introduction

This is a React single page application (SPA) for web browsers. It uses:

- MaterialUI for components
- React Router for view transitions
- Axios for REST API access
- MobX for state management
- i18next for language translations
- Promise tracker for progress feedback

## Steps

1. Install nvm
2. mkdir react-spa
3. cd react-spa
4. echo lts/fermium > .nvmrc
5. nvm i
6. cd ..
7. npx create-react-app react-spa --typescript
8. cd react-spa
9.

```shell
npm i prettier prettier-airbnb-config --save-dev
npm i --save \
    axios \
    @material-ui/core \
    typeface-roboto \
    i18next \
    i18next-browser-languagedetector \
    i18next-http-backend \
    react-i18next \
    mobx \
    mobx-react-lite \
    react-loader-spinner \
    react-promise-tracker \
    react-router \
    react-router-dom
```

11. Follow the instructions for installing
    [airbnb eslint modules](https://www.npmjs.com/package/eslint-config-airbnb-typescript)

12. Create .prettierrc.js

```js
module.exports = {
  ...require('prettier-airbnb-config'),
  printWidth: 120,
};
```

13. Create .prettierignore

```js
build/
node_modules/
```

14. Create .eslintignore

```js
docs/
build/
```

15. Create tsconfig.eslint.json

```js
{
  "extends": "./tsconfig.json",
  "include": ["**/*.ts", "**/*.js", "**/*.jsx", "**/*.tsx", "**/*.js"]
}
```

16. Create .eslintrc.js

```js
module.exports = {
  extends: ['airbnb-typescript', 'react-app/jest'],
  rules: {
    'max-len': [
      'error',
      {
        code: 120,
        ignoreUrls: true,
      },
    ],
  },
};
```

17. Modify package.json

```js
  "scripts": {
    "prettier": "prettier . --write",
    "lint": "npx eslint . --fix --ext .js,.jsx,.ts,.tsx",
```

18. Follow the instructions to [add decorator support](https://www.robinwieruch.de/create-react-app-mobx-decorators)
