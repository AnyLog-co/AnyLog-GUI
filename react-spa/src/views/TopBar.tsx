import React from 'react';
import Grid from '@material-ui/core/Grid';

import UserMenu from '../components/UserButton';
import Language from '../components/Language';

const TopBar: React.FC = () => (
  <Grid justify="space-between" container spacing={3}>
    <Grid item>
      <img src="logo.png" alt="AnyLog" />
    </Grid>
    <Grid item>
      <Language />
    </Grid>
    <Grid item>
      <UserMenu />
    </Grid>
  </Grid>
);

export default TopBar;
