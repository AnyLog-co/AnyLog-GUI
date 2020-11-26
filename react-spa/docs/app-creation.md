# How this app was created

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
    react-router-dom
```

10. Create .prettierignore

```js
node_modules/
```

11. Create .eslintignore

```js
docs/
build/
```

12. Create tsconfig.eslint.json

```js
{
  "extends": "./tsconfig.json",
  "include": ["**/*.ts", "**/*.js", "**/*.jsx", "**/*.tsx", "**/*.js", ".eslintrc.js"]
}
```

13. Create .eslintrc.js

```js
module.exports = {
  extends: ['airbnb-typescript', 'react-app/jest'],
  parserOptions: {
    project: './tsconfig.eslint.json',
  },
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

14. Create .prettierrc.js

```js
module.exports = {
  ...require('prettier-airbnb-config'),
  printWidth: 120
};
```

15. Modify package.json

```js
  "scripts": {
    "prettier": "prettier . --write",
    "lint": "npx eslint . --fix --ext .js,.jsx,.ts,.tsx",
```

16. Follow the instructions to [add decorator support](https://www.robinwieruch.de/create-react-app-mobx-decorators)
