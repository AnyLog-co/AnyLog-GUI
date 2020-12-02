# Developer Guidelines

## Functional Components

- Use React.ReactNode as the type for children

```js
interface Props {
  children?: React.ReactNode;
}
```

## Exporting Multiple Symbols From a Module

Follow React's convention. All exported symbols are collected (by hand) in an object that is defined at the botom of the
module and it is default exported.
