// TODO add prop types
/* eslint-disable react/prop-types */
/* eslint-disable react/destructuring-assignment */
import React from 'react';
import Container from '@material-ui/core/Container';
import { makeStyles } from '@material-ui/core/styles';

import version from '../lib/version';

const useStyles = makeStyles(() => ({
  footer: {
    'text-align': 'right',
    'font-weight': 'bold',
    'font-style': 'italic',
    'font-size': 'small',
    position: 'fixed',
    bottom: 10,
    opacity: 0.1,
  },
}));

const Footer: React.FC = () => {
  const classes = useStyles();
  return (
    <Container maxWidth={false} className={classes.footer}>
      {version}
    </Container>
  );
};

export default Footer;
