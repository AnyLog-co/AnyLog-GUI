import React, { MouseEvent } from "react";

import Button from "@material-ui/core/Button";
import Avatar from "@material-ui/core/Avatar";
import Menu from "@material-ui/core/Menu";
import MenuItem from "@material-ui/core/MenuItem";

const AvatarMenu: React.FC = () => {
  const [anchorEl, setAnchorEl] = React.useState<HTMLButtonElement | undefined>();

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
      <Menu anchorEl={anchorEl} keepMounted open={Boolean(anchorEl)} onClose={handleClose}>
        <MenuItem>Logout</MenuItem>
      </Menu>
    </>
  );
};

export default AvatarMenu;
