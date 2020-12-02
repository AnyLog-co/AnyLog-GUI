import React, { MouseEvent } from 'react';

import Button from '@material-ui/core/Button';
import Avatar from '@material-ui/core/Avatar';
import Menu from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';

import { UserStoreConsumer, UserStore } from './UserStore';

const UserMenu: React.FC = () => {
  const [anchorEl, setAnchorEl] = React.useState<HTMLButtonElement | undefined>();

  const handleClick = (event: MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => setAnchorEl(undefined);

  return (
    <UserStoreConsumer>
      {(userStore: UserStore) => {
        const logout = () => {
          userStore.logout();
        };
        return (
          <Button onClick={handleClick}>
            <Avatar />
            <Menu anchorEl={anchorEl} keepMounted open={Boolean(anchorEl)} onClose={handleClose}>
              <MenuItem onClick={logout}>Logout</MenuItem>
            </Menu>
          </Button>
        );
      }}
    </UserStoreConsumer>
  );
};

export default UserMenu;
