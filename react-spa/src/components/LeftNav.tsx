/* eslint-disable react/prop-types */
/* eslint-disable react/destructuring-assignment */
import React from 'react';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import { makeStyles } from '@material-ui/core/styles';

import ResizableDrawer from './ResizableDrawer';
import UserButton from './UserButton';
import Language from './Language';

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types, react/require-default-props
const LeftNav: React.FC = (props: { children?: React.ReactNode }) => {
  const useStyles = makeStyles((theme) => ({
    root: {
      display: 'flex',
    },
    appBar: {
      zIndex: theme.zIndex.drawer + 1,
    },
    content: {
      flexGrow: 1,
      padding: theme.spacing(3),
    },
    contentShift: {
      transition: theme.transitions.create('margin', {
        easing: theme.transitions.easing.easeOut,
        duration: theme.transitions.duration.enteringScreen,
      }),
      marginRight: 0,
    },
    toolbar: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'flex-end',
      padding: theme.spacing(0, 1),
      // necessary for content to be below app bar
      ...theme.mixins.toolbar,
    },
  }));

  const classes = useStyles();

  return (
    <div className={classes.root}>
      <AppBar position="fixed" className={classes.appBar}>
        <Toolbar>
          <UserButton />
          <Language />
        </Toolbar>
      </AppBar>
      <ResizableDrawer />
      <main className={`$[classes.content} ${classes.contentShift}`}>
        <div className={classes.toolbar} />
        {props.children}
      </main>
    </div>
  );
};

export default LeftNav;
