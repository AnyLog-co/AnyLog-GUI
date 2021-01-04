import React from 'react';
import Grid from '@material-ui/core/Grid';

import LoginC from '../components/Login';
import Language from '../components/Language';

const Login: React.FC = () => (
  <>
    <Grid justifyContent="space-between" container spacing={2}>
      <Grid item>
        <img src="/logo.png" alt="AnyLog" />
      </Grid>
      <Grid item>
        <Language />
      </Grid>
    </Grid>
    <LoginC />
  </>
);

export default Login;
