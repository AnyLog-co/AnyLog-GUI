import React from 'react';
import Menu from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';

import UserContext from './UserContext';

interface Props {
  anchorEl: Element | undefined;
  onClose: () => void;
}

const UserMenu: React.FC<Props> = ({ anchorEl, onClose }) => {
  const { dispatch } = UserContext.use();

  const logout = () => {
    dispatch({ type: 'logout' });
    onClose();
  };

  return (
    <Menu anchorEl={anchorEl} open={!!anchorEl} onClose={onClose}>
      <MenuItem onClick={logout}>Logout</MenuItem>
    </Menu>
  );
};

export default UserMenu;
