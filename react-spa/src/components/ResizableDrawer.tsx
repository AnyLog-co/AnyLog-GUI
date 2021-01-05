// Event handler on a div
/* eslint-disable jsx-a11y/no-static-element-interactions */
import React, { useCallback } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import DnsOutlinedIcon from '@material-ui/icons/DnsOutlined';
import Drawer from '@material-ui/core/Drawer';
import List from '@material-ui/core/List';
import Divider from '@material-ui/core/Divider';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import { useHistory } from 'react-router-dom';

export const defaultDrawerWidth = 240;
const minDrawerWidth = 50;
const maxDrawerWidth = 1000;

const ResizableDrawer: React.FC = () => {
  const history = useHistory();
  const [drawerWidth, setDrawerWidth] = React.useState(defaultDrawerWidth);

  const classes = makeStyles((theme) => ({
    drawer: {
      width: drawerWidth,
      flexShrink: 0,
      whitespace: 'nowrap',
    },
    dragger: {
      width: '5px',
      cursor: 'ew-resize',
      padding: '4px 0 0',
      borderTop: '1px solid #ddd',
      position: 'absolute',
      top: 0,
      right: 0,
      bottom: 0,
      zIndex: 100,
      backgroundColor: '#f4f7f9',
    },
    toolbar: theme.mixins.toolbar,
  }))();

  const handleMouseMove = useCallback((e) => {
    const newWidth = e.clientX - document.body.offsetLeft;
    if (newWidth > minDrawerWidth && newWidth < maxDrawerWidth) {
      setDrawerWidth(newWidth);
    }
  }, []);

  const handleMouseUp = () => {
    document.removeEventListener('mouseup', handleMouseUp, true);
    document.removeEventListener('mousemove', handleMouseMove, true);
  };

  const handleMouseDown = () => {
    document.addEventListener('mouseup', handleMouseUp, true);
    document.addEventListener('mousemove', handleMouseMove, true);
  };

  return (
    <Drawer className={classes.drawer} variant="permanent" PaperProps={{ style: { width: drawerWidth } }}>
      <div className={classes.toolbar} />
      <div onMouseDown={handleMouseDown} className={classes.dragger} />
      <List>
        <ListItem button key="nodes" onClick={() => history.push('/network/nodes')}>
          <ListItemIcon>
            <DnsOutlinedIcon />
          </ListItemIcon>
          <ListItemText primary="Nodes" />
        </ListItem>
      </List>
      <Divider />
    </Drawer>
  );
};

export default ResizableDrawer;
