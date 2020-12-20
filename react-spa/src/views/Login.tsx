/* eslint-disable react/prop-types */
import React, { FC, useReducer, useEffect, KeyboardEvent, MouseEvent, ChangeEventHandler } from 'react';
import { useTranslation, Trans } from 'react-i18next';
import { useRecoilState } from 'recoil';
import { Redirect } from 'react-router';

import { createStyles, makeStyles, Theme } from '@material-ui/core/styles';
import TextField from '@material-ui/core/TextField';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import CardActions from '@material-ui/core/CardActions';
import CardHeader from '@material-ui/core/CardHeader';
import Button from '@material-ui/core/Button';

import ProxyCommunicator from '../lib/ProxyCommunicator';
import Communicator from '../lib/Communicator';
import communicatorState from '../lib/communicatorState';

// @todo Convert layout to Grid
const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    container: {
      display: 'flex',
      flexWrap: 'wrap',
      width: 400,
      margin: `${theme.spacing(0)} auto`,
    },
    loginBtn: {
      marginTop: theme.spacing(2),
      flexGrow: 1,
    },
    header: {
      // Black on white
      textAlign: 'center',
      background: '#212121',
      color: '#fff',
    },
    card: {
      marginTop: theme.spacing(10),
    },
  }),
);

// state type
interface State {
  username: string;
  password: string;
  isButtonDisabled: boolean;
  helperText: string;
  isError: boolean;
  successful: boolean;
}

const initialState: State = {
  username: '',
  password: '',
  isButtonDisabled: true,
  helperText: '',
  isError: false,
  successful: false,
};

type Action =
  | { type: 'setUsername'; payload: string }
  | { type: 'setPassword'; payload: string }
  | { type: 'setIsButtonDisabled'; payload: boolean }
  | { type: 'loginSuccess'; payload: string }
  | { type: 'loginFailed'; payload: string }
  | { type: 'setIsError'; payload: boolean };

const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case 'setUsername':
      return {
        ...state,
        username: action.payload,
      };
    case 'setPassword':
      return {
        ...state,
        password: action.payload,
      };
    case 'setIsButtonDisabled':
      return {
        ...state,
        isButtonDisabled: action.payload,
      };
    case 'loginSuccess':
      return {
        ...state,
        helperText: action.payload,
        isError: false,
        successful: true,
      };
    case 'loginFailed':
      return {
        ...state,
        helperText: action.payload,
        isError: true,
      };
    case 'setIsError':
      return {
        ...state,
        isError: action.payload,
      };
    default: {
      return {
        ...state,
        isError: true,
      };
    }
  }
};

const Login: FC = () => {
  const { t } = useTranslation();

  // TODO if already logged in, ?
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [_, setCommunicator] = useRecoilState<Communicator | undefined>(communicatorState);

  const classes = useStyles();
  const [state, dispatch] = useReducer(reducer, initialState);

  useEffect(() => {
    if (state.username.trim() && state.password.trim()) {
      dispatch({
        type: 'setIsButtonDisabled',
        payload: false,
      });
    } else {
      dispatch({
        type: 'setIsButtonDisabled',
        payload: true,
      });
    }
  }, [state.username, state.password]);

  const handleLogin = () => {
    // @todo Disable the button, run async call to check username and password
    // If unsuccessful, enable the button.
    if (state.username === 'a' && state.password === 'a') {
      setCommunicator(new ProxyCommunicator(state.username, state.password));
      dispatch({
        type: 'loginSuccess',
        payload: 'Login Successfully',
      });
    } else {
      dispatch({
        type: 'loginFailed',
        payload: 'Incorrect username or password',
      });
    }
  };

  const handleKeyPress = (event: KeyboardEvent) => {
    if (event.key === 'Enter' && !state.isButtonDisabled) handleLogin();
  };

  const handleUsernameChange: ChangeEventHandler<HTMLInputElement> = (event) => {
    dispatch({
      type: 'setUsername',
      payload: event.target.value,
    });
  };

  const handlePasswordChange: ChangeEventHandler<HTMLInputElement> = (event) => {
    dispatch({
      type: 'setPassword',
      payload: event.target.value,
    });
  };

  if (state.successful) return <Redirect to="/" />;

  return (
    <form className={classes.container} noValidate autoComplete="off">
      <Card className={classes.card}>
        <CardHeader className={classes.header} title={t('Login.title')} />
        <CardContent>
          <div>
            <TextField
              error={state.isError}
              fullWidth
              id="username"
              type="email"
              label="Username"
              placeholder="Username"
              margin="normal"
              onChange={handleUsernameChange}
              onKeyPress={handleKeyPress}
            />
            <TextField
              error={state.isError}
              fullWidth
              id="password"
              type="password"
              label="Password"
              placeholder="Password"
              margin="normal"
              helperText={state.helperText}
              onChange={handlePasswordChange}
              onKeyPress={handleKeyPress}
            />
          </div>
        </CardContent>
        <CardActions>
          <Button
            variant="contained"
            size="large"
            color="secondary"
            className={classes.loginBtn}
            disabled={state.isButtonDisabled}
            onClick={(event: MouseEvent<HTMLButtonElement>) => {
              // @todo This eliminates a warning that is sent to the console
              event.preventDefault();
              handleLogin();
            }}
          >
            <Trans>Login.button-login</Trans>
          </Button>
        </CardActions>
      </Card>
    </form>
  );
};

export default Login;
