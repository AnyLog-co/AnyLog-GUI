import React, { MouseEvent, useState } from 'react';
import Avatar from '@material-ui/core/Avatar';
import Button from '@material-ui/core/Button';
import Tooltip from '@material-ui/core/Tooltip';

import UserContext from './UserContext';
import UserMenu from './UserMenu';

/**
 * @description A button in the shape of the user's avatar that opens a menu when clicked
 */
const UserButton: React.FC = () => {
  // eslint-disable-next-line prefer-const
  let [anchorEl, setAnchorEl] = useState<HTMLButtonElement | undefined>();

  const handleClick = (event: MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(undefined);
  };

  const { state } = UserContext.use();

  return (
    <>
      <Tooltip title={state.username}>
        <Button onClick={handleClick}>
          <Avatar />
        </Button>
      </Tooltip>
      <UserMenu anchorEl={anchorEl} onClose={handleClose} />
    </>
  );
};

export default UserButton;
