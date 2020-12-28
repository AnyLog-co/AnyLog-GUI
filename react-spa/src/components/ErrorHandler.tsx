/* eslint-disable react/destructuring-assignment */
import React from 'react';

interface Props {
  children: React.ReactNode;
}

interface State {
  errorOccurred: boolean;
  error?: Error;
  info?: string;
}

class ErrorHandler extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { errorOccurred: false, error: undefined, info: undefined };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo): void {
    const infoStr = JSON.stringify(info);
    // eslint-disable-next-line no-console
    console.log(`Error: ${error.message}\n${infoStr}`);
    this.setState({ errorOccurred: true, error, info: infoStr });
  }

  render(): React.ReactNode {
    // eslint-disable-next-line react/destructuring-assignment
    return this.state.errorOccurred ? (
      <>
        <h1>Error: {this.state.error?.message}</h1>
        <h5>{this.state.info}</h5>
      </>
    ) : (
      this.props.children
    );
  }
}

export default ErrorHandler;
