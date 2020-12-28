# Introduction

This React-based single-page application was built using [Create React App](https://create-react-app.dev/) in October 2020.

## Features

- React Hooks
- Typescript
- [Prettier and ESLint using Airbnb Style Guide](https://terrislinenbach.medium.com/formatting-and-linting-a-modern-react-typescript-project-fa127e6426f)
- [Material-UI](https://material-ui.com/) version 5 components (still alpha)
- Page transitions via [React Router](https://reactrouter.com/)
- External data retrieval via [React Query](https://react-query.tanstack.com/) version 3
- Tabular data display via [React Table](https://react-table.tanstack.com/)
- Global state management via [Recoil](https://recoiljs.org/)
- "Loading" feedback via [React Suspense](https://reactjs.org/docs/concurrent-mode-suspense.html)
- Translations via [i18next](https://www.i18next.com/)
- [CORS workaround proxy](https://terrislinenbach.medium.com/an-advanced-cors-workaround-for-react-apps-40dec1a4a0cd)
- A default error page
- A custom 404 page
- Testing with Jest and React Testing Library
  - A sample test invokes an external service
  - Because the example uses the proxy, you must start the app (npm run start) prior to running tests

## How this app was created

1. [Install nvm](https://heynode.com/tutorial/install-nodejs-locally-nvm)
2. `nvm i lts/fermium`
3. `npx create-react-app react-spa --typescript`
4. `cd react-spa`
5. `echo lts/fermium > .nvmrc`

6.

```shell
npm i --save-dev eslint prettier eslint-config-airbnb-typescript-prettier typescript

npm i --save \
  i18next i18next-browser-languagedetector i18next-http-backend react-i18next \
  react-loader-spinner @types/react-loader-spinner \
  recoil \
  react-dom @types/react-dom \
  react-router @types/react-router \
  react-router-dom @types/react-router-dom \
  react-query @types/react-query \
  react-table @types/react-table \
  jest-localstorage-mock \
  request

# Material-UI 5
npm i --save \
  typeface-roboto \
  @material-ui/lab @emotion/react @emotion/styled @material-ui/core@next typeface-roboto
```

7. Create .eslintrc.js

```js
// For gatsby config, see https://github.com/d4rekanguok/gatsby-typescript/blob/master/.eslintrc.js
module.exports = {
  overrides: [
    {
      // Plain JavaScript
      files: ['*.{js,jsx}'],
      extends: ['airbnb', 'airbnb/hooks', 'prettier', 'prettier/react', 'react-app', 'react-app/jest'],
      plugins: ['prettier'],
    },
    {
      // Typescript
      // See https://github.com/toshi-toma/eslint-config-airbnb-typescript-prettier/blob/master/index.js
      files: ['*.{ts,tsx}'],
      extends: ['airbnb-typescript-prettier', 'react-app', 'react-app/jest'],
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

8. Create .eslintignore

```js
# node_modules is ignored by default
build/
dist/
docs/
```

9. Create .prettierrc.js

```js
module.exports = {
  printWidth: 120,
  singleQuote: true,
  trailingComma: 'all',
};
```

10. Create .prettierignore

```js
build/
dist/
node_modules/
```

11. Modify package.json

11.1 Remove eslint section

11.2 Add format and lint scripts

```js
  "scripts": {
    "lint": "tsc --noEmit && eslint --fix '*.{js,jsx,ts,tsx}'"
    "format": "prettier . --write",
```

12. Edit tsconfig.json

- set compilerOptions.target to esnext

## Appendix

### (Ac)Knowledgements

This app was made possible by the contributions of many developers who kindly shared their knowledge, free of charge. I regret that not every reference has been cited. Here is a [list of references](tech-references.md) that were invaluable for building this project.

### Should @types/\* appear in devDependencies?

Because React applications are bundled, it doesn't matter whether you use devDependencies. All dependencies are considered at build time. Modules that aren't needed are discarded. If you're building a reusable library, not including a @types module can cause issues for the module's users [see also](https://github.com/facebook/create-react-app/issues/6180#issuecomment-453640473).
