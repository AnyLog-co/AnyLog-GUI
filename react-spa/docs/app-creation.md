# How this app was created

## Introduction

This is a React single page application (SPA) for web browsers. It uses:

- React Hooks with React 17
- Typescript 4.1
- Material-UI Components
- React Router
- MobX for state management
- Axios for REST API access
- i18next for translations
- Promise tracker for 'loading' feedback (three dots, animated)

## Steps

1. [Install nvm](https://heynode.com/tutorial/install-nodejs-locally-nvm)
2. `mkdir react-spa`
3. `cd react-spa`
4. `echo lts/fermium > .nvmrc`
5. `nvm i`
6. `cd ..`
7. `npx create-react-app react-spa --typescript`

8. `cd react-spa`

9.

```shell
npm i --save-dev typescript eslint prettier eslint-config-airbnb-typescript-prettier \
  enzyme enzyme-adapter-react-16 react-test-renderer

npm i --save \
  axios \
  @material-ui/core \
  typeface-roboto \
  i18next \
  i18next-browser-languagedetector \
  i18next-http-backend \
  react-i18next \
  mobx \
  mobx-react \
  react-loader-spinner \
  @types/react-loader-spinner \
  react-promise-tracker \
  react-router \
  @types/react-router \
  react-router-dom \
  @types/react-router-dom
```

10. Create .eslintrc.js

```js
module.exports = {
  extends: ['airbnb-typescript-prettier', 'airbnb/hooks', 'prettier/react', 'react-app/jest'],
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

11. Create .eslintignore

```js
# node_modules is ignored by default
build/
dist/
docs/
```

12. Create .prettierrc.js

```js
module.exports = {
  printWidth: 120,
  singleQuote: true,
  trailingComma: 'all',
};
```

13. Create .prettierignore

```js
build/
dist/
node_modules/
```

14. Modify package.json and add format and lint scripts

```js
  "scripts": {
    "lint": "tsc --noEmit && eslint --fix 'src/*.{js,jsx,ts,tsx}'"
    "format": "prettier . --write",
```

15. Edit tsconfig.json

- set compilerOptions.target to es2020

16. To support Typescript 4.1

16.1 Edit package.json and modify the babel section:

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

16.2 Edit react-app-env.d.ts and add:

```js
declare module 'react/jsx-runtime' {
  export default any;
}
```
