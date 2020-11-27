module.exports = {
  extends: [
    "airbnb-typescript",
    "airbnb/hooks",
    "plugin:@typescript-eslint/recommended",
    "plugin:jest/recommended",
    "prettier",
    "prettier/react",
    "prettier/@typescript-eslint",
    "plugin:prettier/recommended",
    "react-app/jest",
  ],
  parserOptions: {
    project: "./tsconfig.eslint.json",
  },
  rules: {
    "max-len": [
      "error",
      {
        code: 120,
        ignoreUrls: true,
      },
    ],
  },
};
