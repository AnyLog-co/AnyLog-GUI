import React from 'react';
import { useQuery } from 'react-query';
import { useRecoilState } from 'recoil';
import CssBaseline from '@material-ui/core/CssBaseline';

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
    <>
      <CssBaseline />
      <Table columns={columns} data={data} />
    </>
  );
};

export default Nodes;
