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
