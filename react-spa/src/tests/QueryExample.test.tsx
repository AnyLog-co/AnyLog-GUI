import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClientProvider, QueryClient } from 'react-query';

import QueryExample from '../components/QueryExample';

it('calls external service', async () => {
  render(
    <QueryClientProvider client={new QueryClient()}>
      <QueryExample />
    </QueryClientProvider>,
  );
  // Use something like this to wait and dump elements
  // await new Promise((resolve)=>setTimeout(resolve, 5000)); screen.degbug();
  await waitFor(() => expect(screen.getByText(/Hooks for fetching/)).toBeInTheDocument());
});
