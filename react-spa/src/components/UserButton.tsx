import React, { MouseEvent, useState } from 'react';

import Button from '@material-ui/core/Button';
import Avatar from '@material-ui/core/Avatar';

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

  return (
    <>
      <Button onClick={handleClick}>
        <Avatar />
      </Button>
      <UserMenu anchorEl={anchorEl} onClose={handleClose} />
    </>
  );
};

export default UserButton;
