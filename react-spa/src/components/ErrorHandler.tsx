/* eslint-disable react/destructuring-assignment */
import React from 'react';

interface Props {
  children: React.ReactNode;
}

interface State {
  errorOccurred: boolean;
  error: Error | undefined;
  info: React.ErrorInfo | undefined;
}

class ErrorHandler extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { errorOccurred: false, error: undefined, info: undefined };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo): void {
    this.setState({ errorOccurred: true, error, info });
  }

  render(): React.ReactNode {
    // eslint-disable-next-line react/destructuring-assignment
    return this.state.errorOccurred ? (
      <>
        <h1>Error</h1>
        <h2>{this.state.error?.message}</h2>
        <h2>{this.state.info}</h2>
      </>
    ) : (
      this.props.children
    );
  }
}

export default ErrorHandler;
