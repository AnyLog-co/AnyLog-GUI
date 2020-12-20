import React from 'react';
import Grid from '@material-ui/core/Grid';
import { useRecoilState } from 'recoil';

import UserButton from '../components/UserButton';
import Language from '../components/Language';
import communicatorState from '../lib/communicatorState';

const Header: React.FC = () => {
  const [communicator] = useRecoilState(communicatorState);

  return (
    <Grid justifyContent="space-between" container spacing={3}>
      <Grid item>
        <img src="logo.png" alt="AnyLog" />
      </Grid>
      <Grid item>
        <Language />
      </Grid>
      <Grid item>{communicator ? <UserButton /> : <></>}</Grid>
    </Grid>
  );
};

export default Header;
