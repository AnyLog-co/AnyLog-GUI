import React, { MouseEvent, useState } from 'react';
import Avatar from '@material-ui/core/Avatar';
import Button from '@material-ui/core/Button';
import Tooltip from '@material-ui/core/Tooltip';
import { useRecoilState } from 'recoil';

import communicatorState, { OptionalCommunicator } from '../lib/communicatorState';
import UserMenu from './UserMenu';

/**
 * @description A button in the shape of the user's avatar that opens a menu when clicked
 */
const UserButton: React.FC = () => {
  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | undefined>();
  const [communicator] = useRecoilState<OptionalCommunicator>(communicatorState);

  const handleClick = (event: MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(undefined);
  };

  return (
    <>
      <Tooltip title={communicator?.username || ''}>
        <Button onClick={handleClick}>
          <Avatar />
        </Button>
      </Tooltip>
      <UserMenu anchorEl={anchorEl} onClose={handleClose} />
    </>
  );
};

export default UserButton;
