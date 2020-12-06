// For jest and gatsby config, see https://github.com/d4rekanguok/gatsby-typescript/blob/master/.eslintrc.js
module.exports = {
  overrides: [
    {
      // Plain JavaScript
      files: ['*.{js,jsx}'],
      extends: ['airbnb', 'airbnb/hooks', 'prettier', 'prettier/react'],
      plugins: ['prettier'],
    },
    {
      // Typescript
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
