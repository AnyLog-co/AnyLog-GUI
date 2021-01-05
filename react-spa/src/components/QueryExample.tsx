/* eslint-disable jsx-a11y/anchor-is-valid */
import React from 'react';
import { useQuery } from 'react-query';
import Loading from './LoadingDots';

import isDev from '../lib/isDev';

const QueryExample: React.FC = () => {
  const { error, data } = useQuery('queryExample', () => {
    let request: Request;
    const url = 'https://api.github.com/repos/tannerlinsley/react-query';

    if (isDev) {
      const headers = new Headers({
        'X-Forward': url,
      });

      request = new Request('/forward', {
        headers,
      });
    } else {
      request = new Request(url);
    }

    return new Promise((res) => setTimeout(res, 5000)).then(() => fetch(request)).then((res) => res.json());
  });

  if (error) {
    // eslint-disable-next-line no-console
    console.error(error);
    throw error;
  }

  if (!data) return <Loading />;

  return (
    <>
      <h1>{data.name}</h1>
      <p>{data.description}</p>
      <strong>👀 {data.subscribers_count}</strong>
      <strong>✨ {data.stargazers_count}</strong>
      <strong>🍴 {data.forks_count}</strong>
    </>
  );
};

export default QueryExample;
