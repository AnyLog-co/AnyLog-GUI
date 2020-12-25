/* eslint-disable jsx-a11y/anchor-is-valid */
import React, { FC } from 'react';
import { useQuery } from 'react-query';

const Example: FC = () => {
  const { isLoading, error, data } = useQuery('repoData', () => {
    const myHeaders = new Headers({
      location: 'https://api.github.com/repos/tannerlinsley/react-query',
    });

    const myRequest = new Request('/api', {
      method: 'GET',
      headers: myHeaders,
    });

    return fetch(myRequest).then((res) => res.json());
  });

  if (isLoading) return <>Loading...</>;
  if (error) throw error;

  console.log(data);
  return (
    <div>
      <h1>{data.name}</h1>
      <p>{data.description}</p>
      <strong>👀 {data.subscribers_count}</strong> <strong>✨ {data.stargazers_count}</strong>{' '}
      <strong>🍴 {data.forks_count}</strong>
    </div>
  );
};

export default Example;
