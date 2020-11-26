module.exports = {
  extends: ['airbnb-typescript'],
  // "react-app/jest"
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
