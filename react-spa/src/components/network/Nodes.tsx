/* eslint-disable react/button-has-type */
import React from 'react';
import { useRecoilState } from 'recoil';
import { useQuery, QueryErrorResetBoundary } from 'react-query';
import { ErrorBoundary } from 'react-error-boundary';

import Table from '../Table';
import communicatorState, { OptionalCommunicator } from '../../lib/Communicator/state';
import Loading from '../LoadingDots';

const columns = [
  {
    Header: 'Company',
    accessor: 'company',
  },
  {
    Header: 'Cluster',
    accessor: 'cluster',
  },
  {
    Header: 'Type',
    accessor: 'type',
  },
  {
    Header: 'Status',
    accessor: 'status',
  },
  {
    Header: 'Name',
    accessor: 'name',
  },
  {
    Header: 'Host Name',
    accessor: 'hostname',
  },
  {
    Header: 'IP Address',
    accessor: 'ip',
  },
  {
    Header: 'Local IP Address',
    accessor: 'local ip',
  },
  {
    Header: 'Port',
    accessor: 'port',
  },
];

const Nodes: React.FC = () => {
  const [communicator] = useRecoilState<OptionalCommunicator>(communicatorState);
  if (!communicator) throw new Error('Not authenticated');

  const { data, error } = useQuery('nodes', () => communicator.nodes());

  if (error) throw error;
  if (!data) return <Loading />;

  return (
    <QueryErrorResetBoundary>
      {({ reset }) => (
        <ErrorBoundary
          // eslint-disable-next-line @typescript-eslint/no-shadow
          fallbackRender={({ error, resetErrorBoundary }) => (
            <>
              There was an error! <button onClick={() => resetErrorBoundary()}>Try again</button>
              <pre style={{ whiteSpace: 'normal' }}>{error.message}</pre>
            </>
          )}
          onReset={reset}
        >
          <Table columns={columns} data={data} />
        </ErrorBoundary>
      )}
    </QueryErrorResetBoundary>
  );
};

export default Nodes;
