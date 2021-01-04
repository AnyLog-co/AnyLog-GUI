import React from 'react';
import Menu from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';
import { useHistory } from 'react-router-dom';

interface Props {
  anchorEl: Element | undefined;
  onClose: () => void;
}

const UserMenu: React.FC<Props> = ({ anchorEl, onClose }) => {
  const history = useHistory();

  return (
    <Menu anchorEl={anchorEl} open={!!anchorEl} onClose={onClose}>
      <MenuItem
        onClick={() => {
          history.push('/logout');
          onClose();
        }}
      >
        Logout
      </MenuItem>
    </Menu>
  );
};

export default UserMenu;
