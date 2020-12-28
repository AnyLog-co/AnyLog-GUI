import React from 'react';
import Menu from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';
import { useRecoilState } from 'recoil';

import communicatorState, { OptionalCommunicator } from '../lib/communicatorState';

interface Props {
  anchorEl: Element | undefined;
  onClose: () => void;
}

const UserMenu: React.FC<Props> = ({ anchorEl, onClose }) => {
  const [communicator, setCommunicator] = useRecoilState<OptionalCommunicator>(communicatorState);

  const logout = () => {
    if (communicator) {
      // TODO
      // communicator.logout();
      localStorage.removeItem('communicator');
      setCommunicator(undefined);
    }
    onClose();
  };

  return (
    <Menu anchorEl={anchorEl} open={!!anchorEl} onClose={onClose}>
      <MenuItem onClick={logout}>Logout</MenuItem>
    </Menu>
  );
};

export default UserMenu;
