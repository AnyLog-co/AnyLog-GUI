import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClientProvider } from 'react-query';

import QueryExample from '../components/QueryExample';
import queryClient from '../lib/queryClient';

it('calls external service', async () => {
  render(
    <QueryClientProvider client={queryClient}>
      <QueryExample />
    </QueryClientProvider>,
  );
  // Use something like this to wait and dump elements
  // await new Promise((resolve)=>setTimeout(resolve, 5000)); screen.degbug();
  await waitFor(() => expect(screen.getByText(/Hooks for fetching/)).toBeInTheDocument());
});
