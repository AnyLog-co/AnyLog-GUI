import React from 'react';
import Grid from '@material-ui/core/Grid';

import UserButton from '../components/UserButton';
import Language from '../components/Language';
import UserContext from '../components/UserContext';

const Header: React.FC = () => {
  const { state } = UserContext.use();

  return (
    <Grid justifyContent="space-between" container spacing={3}>
      <Grid item>
        <img src="logo.png" alt="AnyLog" />
      </Grid>
      <Grid item>
        <Language />
      </Grid>
      <Grid item>{state.authenticated ? <UserButton /> : <></>}</Grid>
    </Grid>
  );
};

export default Header;
