import React from 'react';
import { useHistory } from 'react-router-dom';
import Menu from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';

import { useUserContext } from './UserContext';

interface Props {
  anchorEl: Element | undefined;
  onClose: () => void;
}

const UserMenu: React.FC<Props> = ({ anchorEl, onClose }) => {
  const userStore = useUserContext();
  const history = useHistory();

  const logout = () => {
    userStore.logout();
    // eslint-disable-next-line no-console
    console.log('logout');
    history.push('/');
    onClose();
  };

  return (
    <Menu anchorEl={anchorEl} open={!!anchorEl} onClose={onClose}>
      <MenuItem onClick={logout}>Logout</MenuItem>
    </Menu>
  );
};

export default UserMenu;
