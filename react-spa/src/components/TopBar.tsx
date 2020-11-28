import React from "react";

import Grid from "@material-ui/core/Grid";
import AvatarMenu from "./AvatarMenu";
import Language from "./Language";

const TopBar = () => (
  <Grid justify="space-between" container spacing={3}>
    <Grid item>
      <img src="logo.png" alt="AnyLog" />
    </Grid>
    <Grid item>
      <Language />
    </Grid>
    <Grid item>
      <AvatarMenu />
    </Grid>
  </Grid>
);

export default TopBar;
