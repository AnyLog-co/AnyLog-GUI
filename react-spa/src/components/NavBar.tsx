import React, { Component } from "react";
import { Link } from "react-router-dom";
import { AppBar, Toolbar, Button, Typography } from "@material-ui/core";

import { logout } from "../actions/auth";

class NavBar extends Component {
  render() {
    return (
      <AppBar position="static" style={{ display: "flex" }}>
        <Toolbar>
          <Typography variant="h6">My App</Typography>
          <div style={{ marginLeft: "auto" }}>
            {this.props.isAuthUser ? (
              <>
                <Link to="/home">
                  <Button color="inherit">Home</Button>
                </Link>
                <Link to="/my-account">
                  <Button color="inherit">My Account</Button>
                </Link>
                <Button color="inherit" onClick={this.props.logout}>
                  Logout
                </Button>
              </>
            ) : (
              <Link to="/login">
                <Button color="inherit">Login</Button>
              </Link>
            )}
          </div>
        </Toolbar>
      </AppBar>
    );
  }
}
