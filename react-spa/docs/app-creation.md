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
npm i --save-dev typescript eslint prettier eslint-config-airbnb-typescript-prettier \
  enzyme enzyme-adapter-react-16 react-test-renderer \
  @babel/preset-react

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
  @types/react-loader-spinner \
  react-promise-tracker \
  react-router \
  @types/react-router \
  react-router-dom \
  @types/react-router-dom
```

10. Create tsconfig.eslint.json

```js
{
  "extends": "./tsconfig.json",
  "include": ["**/*.ts", "**/*.js", "**/*.jsx", "**/*.tsx", "**/*.js"]
}
```

11. Create .eslintrc.js

```js
module.exports = {
  extends: ['airbnb-typescript-prettier', 'airbnb/hooks', 'prettier/react', 'react-app/jest'],
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

12. Create .eslintignore

```js
# node_modules is ignored by default
.eslintrc.js
docs/
build/
```

13. Create .prettierrc.js

```js
module.exports = {
  printWidth: 120,
  singleQuote: true,
  trailingComma: 'all',
};
```

14. Create .prettierignore

```js
build/
node_modules/
```

15. Modify package.json and add format and lint:fix scripts

```js
  "scripts": {
    "lint": "tsc --project tsconfig.eslint.json --noEmit && eslint --fix './src/**/*.{ts,tsx}'",
    "format": "prettier . --write",
```

16. Follow the instructions to [add decorator support](https://www.robinwieruch.de/create-react-app-mobx-decorators)

17. Edit tsconfig.json

- set compilerOptions.target to es2020

18. To support Typescript 4.1, Edit package.json and set the babel section:

```js
  "babel": {
    "presets": [
      [
        "@babel/preset-react",
        {
          "runtime": "automatic"
        }
      ]
    ]
  }
```

19. To support Typescript 4.1, react-app-env.d.ts and add:

```js
declare module 'react/jsx-runtime' {
  export default any;
}
```
