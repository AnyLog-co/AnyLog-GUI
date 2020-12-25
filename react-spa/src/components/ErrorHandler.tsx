import React from 'react';

interface Props {
  children: React.ReactNode;
}

interface State {
  errorOccurred: boolean;
}

class ErrorHandler extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { errorOccurred: false };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo): void {
    this.setState({ errorOccurred: true });
    console.log(error);
    console.log(info);
  }

  render(): React.ReactNode {
    // eslint-disable-next-line react/destructuring-assignment
    return this.state.errorOccurred ? <h1>Something went wrong!</h1> : this.props.children;
  }
}

export default ErrorHandler;
