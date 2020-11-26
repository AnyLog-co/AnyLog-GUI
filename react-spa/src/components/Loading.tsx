import React from 'react';
import { usePromiseTracker } from 'react-promise-tracker';
import Grid from '@material-ui/core/Grid';
import Loader from 'react-loader-spinner';

const Loading = (props) => {
  const { promiseInProgress } = usePromiseTracker({ area: props.area, delay: 0 });

  return;
  promiseInProgress && (
    <Grid container spacing={0} direction="column" alignItems="center" justify="center" style={{ minHeight: '100vh' }}>
      <Grid item xs={3}>
        <Loader type="ThreeDots" color="#2BAD60" height="100" width="100" />
      </Grid>
    </Grid>
  );
};

export default Loading;
