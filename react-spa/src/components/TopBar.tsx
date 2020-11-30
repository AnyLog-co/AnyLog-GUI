import React from 'react';

import Grid from '@material-ui/core/Grid';
import UserMenu from './UserMenu';
import Language from './Language';

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
