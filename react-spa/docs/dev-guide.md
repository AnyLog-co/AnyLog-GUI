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

## async

If a function returns a Promise, it should be tagged as async. Technically, async isn’t needed if the function doesn’t
throw exceptions or use await. This
[article](https://makandracards.com/makandra/43653-javascript-don-t-throw-exceptions-from-async-functions) does a pretty
good job of explaining why: `then()` and `catch()` don’t handle synchronous exceptions. The author however fails to
mention that all you need to do is mark the function ‘async,’ which causes exceptions to automatically be converted to
Promises, avoiding the need to call `Promise.reject()`.

## Visual Studio Code

### Starting Visual Studio Code

Before starting vscode, configure environment variables for:

- NodeJS engine
- Github identity

#### OSX and Linux

```bash
#!/bin/sh

git config --global user.name "your-github-username"
git config --global user.email "your-github-email-address"
export GIT_SSH_COMMAND="ssh -i ~/.ssh/your-github-private-ssh-key"
```

##### OSX

Add this to the above script

```bash
. $(brew --prefix nvm)/nvm.sh
nvm i
code .
```

### Recommended Extensions

1. ESLint
2. GitLens
3. Git Graph
4. GitHub Pull Requests and Issues
5. vscode-journal
6. vscode-journal-view
7. Bracket Pair Colorizer 2
8. Guides
9. Todo Tree

### Typescript Version

- [Use the Typescript version associated with this project (as defined in package.json)](https://gist.github.com/tonysneed/bb6d442103a057578a9498f106e45ac5)

### Typescript Syntax Highlighting

If VSCode does not recognize .tsx files for syntax highlighting, etc.:

1. Click Extensions in the left navigation bar
2. Search for "@builtin typescript"
3. Make sure all extensions listed are enabled

## Recommended Chrome Extensions

- [React Developer Tools](https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi?hl=en)
