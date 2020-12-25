# How this app was created

## Introduction

This is a React 17 single page application (SPA) for web browsers. It features:

- Modern React development with hooks
- Typescript
- [Prettier and ESLint](https://terrislinenbach.medium.com/formatting-and-linting-a-modern-react-typescript-project-fa127e6426f)
- Material-UI look and feel (version 5, alpha)
- Data access via React Query 3 and Axios
- Global state management via Recoil
- "Loading" feedback via React Suspense
- Page transitions via React Router
- i18next for translations
- [CORS workaround proxy](https://terrislinenbach.medium.com/an-advanced-cors-workaround-for-react-apps-40dec1a4a0cd)
- A default error page
- A custom 404 page
- Testing with Jest and React Testing Library
  - A sample test invokes an external service is included
  - Because the example uses the proxy, you must start the app (npm run start) prior to running tests

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
npm i --save-dev eslint prettier eslint-config-airbnb-typescript-prettier jest-localstorage-mock

npm i --save \
  axios \
  i18next i18next-browser-languagedetector i18next-http-backend react-i18next \
  react-loader-spinner @types/react-loader-spinner recoil \
  react-router @types/react-router \
  react-router-dom @types/react-router-dom \
  # Material-UI 5
  @emotion/react @emotion/styled @material-ui/core@next typeface-roboto \
  react-query @types/react-query \
  react-table @types/react-table
```

10. Create .eslintrc.js

```js
// For jest and gatsby config, see https://github.com/d4rekanguok/gatsby-typescript/blob/master/.eslintrc.js
module.exports = {
  overrides: [
    {
      // JavaScript and JSX
      files: ['*.{js,jsx}'],
      extends: ['airbnb', 'airbnb/hooks', 'prettier', 'prettier/react'],
      plugins: ['prettier'],
    },
    {
      // Typescript and TSX
      // See https://github.com/toshi-toma/eslint-config-airbnb-typescript-prettier/blob/master/index.js
      files: ['*.{ts,tsx}'],
      extends: ['airbnb-typescript-prettier'],
    },
  ],
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
    "lint": "tsc --noEmit && eslint --fix '*.{js,jsx,ts,tsx}'"
    "format": "prettier . --write",
```

15. Edit tsconfig.json

- set compilerOptions.target to esnext

# Should @types/\* appear in devDependencies?

Because React applications are bundled, it doesn't matter whether you use devDependencies. All dependencies are considered at build time. Modules that aren't needed are discarded. If you're building a reusable library, not including a @types module can cause issues for the module's users. [Reference](https://github.com/facebook/create-react-app/issues/6180#issuecomment-453640473).
