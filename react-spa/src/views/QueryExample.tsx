/* eslint-disable jsx-a11y/anchor-is-valid */
import React, { FC } from 'react';
import { useQuery, QueryCache, ReactQueryCacheProvider } from 'react-query';

const queryCache = new QueryCache();

const Example: FC = () => {
  const { isLoading, error, data } = useQuery('repoData', () =>
    fetch('https://api.github.com/repos/tannerlinsley/react-query').then((res) => res.json()),
  );

  if (isLoading) return <>Loading...</>;

  if (error) throw error;

  return (
    <div>
      <h1>{data.name}</h1>
      <p>{data.description}</p>
      <strong>👀 {data.subscribers_count}</strong> <strong>✨ {data.stargazers_count}</strong>{' '}
      <strong>🍴 {data.forks_count}</strong>
    </div>
  );
};

const QueryExample: FC = () => (
  <ReactQueryCacheProvider queryCache={queryCache}>
    <Example />
  </ReactQueryCacheProvider>
);

export default QueryExample;
