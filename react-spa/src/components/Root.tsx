/* eslint-disable react/button-has-type */
import React, { Suspense } from 'react';
import { ReactQueryDevtools } from 'react-query/devtools';
import { QueryClientProvider, QueryErrorResetBoundary } from 'react-query';
import { useRecoilState } from 'recoil';
import { ErrorBoundary } from 'react-error-boundary';

import Header from './Header';
import Routes from './Routes';
import qc from '../lib/queryClient';
import communicatorState from '../lib/Communicator/state';
import Loading from './LoadingDots';

const QueryRoot: React.FC = () => {
  const [communicator] = useRecoilState(communicatorState);
  const queryClient = communicator ? communicator.queryClient : qc();

  return (
    <QueryClientProvider client={queryClient}>
      <Suspense fallback={<Loading />}>
        <Header />
        <QueryErrorResetBoundary>
          {({ reset }) => (
            <ErrorBoundary
              fallbackRender={({ error, resetErrorBoundary }) => (
                <>
                  There was an error! <button onClick={() => resetErrorBoundary()}>Try again</button>
                  <pre style={{ whiteSpace: 'normal' }}>{error.message}</pre>
                </>
              )}
              onReset={reset}
            >
              <Routes />
            </ErrorBoundary>
          )}
        </QueryErrorResetBoundary>
      </Suspense>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
};

export default QueryRoot;
