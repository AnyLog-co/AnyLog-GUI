import React from 'react';
import Menu from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';
import { useRecoilState } from 'recoil';
import { useHistory } from 'react-router-dom';

import Communicator from '../lib/Communicator';
import communicatorState from '../lib/communicatorState';

interface Props {
  anchorEl: Element | undefined;
  onClose: () => void;
}

const UserMenu: React.FC<Props> = ({ anchorEl, onClose }) => {
  const [communicator, setCommunicator] = useRecoilState<Communicator | undefined>(communicatorState);
  const history = useHistory();

  const logout = () => {
    if (communicator) {
      // communicator.logout();
      history.push('/');
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
