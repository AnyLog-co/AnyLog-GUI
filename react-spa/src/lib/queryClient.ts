import { QueryClient } from 'react-query';

export default (): QueryClient =>
  new QueryClient({
    defaultOptions: {
      queries: {
        suspense: true,
      },
    },
  });
