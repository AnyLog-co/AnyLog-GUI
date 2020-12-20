import React from 'react';
import Grid from '@material-ui/core/Grid';
import Loader from 'react-loader-spinner';

const LoadingDots: React.FC = () => {
  return (
    <Grid container justifyContent="center">
      <Grid item>
        <Loader type="ThreeDots" color="#2BAD60" height={100} width={100} />
      </Grid>
    </Grid>
  );
};

export default LoadingDots;
