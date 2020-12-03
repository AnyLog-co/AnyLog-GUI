# Developer Guidelines

## Functional Components

- All props must have interfaces
- Use React.FC (controversial but it's a time saver)
- Use React.ReactNode as the type for children

```js
interface Props {
  children?: React.ReactNode;
}
```
