/* eslint-disable jsx-a11y/anchor-is-valid */
import React, { FC } from 'react';
import { useQuery } from 'react-query';

import Loading from './LoadingDots';
import isDev from '../lib/isDev';

const QueryExample: FC = () => {
  const { isLoading, error, data } = useQuery('repoData', () => {
    let request;
    const url = 'https://api.github.com/repos/tannerlinsley/react-query';

    if (isDev) {
      const headers = new Headers({
        'X-Forward': url,
      });

      request = new Request('/external', {
        headers,
      });
    } else {
      request = new Request(url);
    }

    return fetch(request).then((res) => res.json());
  });

  if (isLoading) return <Loading />;
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

export default QueryExample;
