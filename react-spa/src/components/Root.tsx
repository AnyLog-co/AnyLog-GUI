import React, { Suspense } from 'react';
import { ReactQueryDevtools } from 'react-query/devtools';
import { QueryClientProvider } from 'react-query';
import { useRecoilState } from 'recoil';

// import Header from './Header';
import Routes from './Routes';
import qc from '../lib/queryClient';
import communicatorState from '../lib/Communicator/state';
import Loading from './LoadingDots';

const Root: React.FC = () => {
  const [communicator] = useRecoilState(communicatorState);
  const queryClient = communicator ? communicator.queryClient : qc();

  return (
    <Suspense fallback={<Loading />}>
      <QueryClientProvider client={queryClient}>
        <Routes />
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    </Suspense>
  );
};

export default Root;
