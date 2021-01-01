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
import Autocomplete from '@material-ui/lab/Autocomplete';

import ProxyCommunicator from '../lib/Communicator/ProxyCommunicator';
import CommunicatorSerDe from '../lib/Communicator/CommunicatorSerDe';
import communicatorState, { OptionalCommunicator } from '../lib/communicatorState';

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
  url: string;
  isButtonDisabled: boolean;
  helperText: string;
  isError: boolean;
}

let urls: string[] = [];

function readUrls() {
  const data = localStorage.getItem('urls');
  if (data) {
    try {
      urls = JSON.parse(data);
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log(error);
      localStorage.removeItem('urls');
    }
  }
  if (!urls.length) {
    urls.push('http://172.105.117.98:2249');
  }
}

function addUrl(url: string): void {
  if (urls.length) {
    const index = urls.indexOf(url);
    if (index > -1) urls.splice(index, 1);
    urls.sort();
  }
  urls.unshift(url);
  localStorage.setItem('urls', JSON.stringify(urls));
}

readUrls();

const initialState: State = {
  username: '',
  password: '',
  url: '',
  isButtonDisabled: true,
  helperText: '',
  isError: false,
};

type Action =
  | { type: 'setUsername'; payload: string }
  | { type: 'setPassword'; payload: string }
  | { type: 'setUrl'; payload: string }
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
    case 'setUrl':
      return {
        ...state,
        url: action.payload,
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

  // eslint-disable-next-line @typescript-eslint/no-unused-vars, prefer-const
  const [communicator, setCommunicator] = useRecoilState<OptionalCommunicator>(communicatorState);

  const classes = useStyles();

  if (urls.length) [initialState.url] = urls;
  const [state, dispatch] = useReducer(reducer, initialState);

  useEffect(() => {
    if (state.username.trim() && state.password.trim() && state.url.trim()) {
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
  }, [state.username, state.password, state.url]);

  const handleLogin = () => {
    // TODO: Disable the button, run async call to check username and password.
    // If unsuccessful, enable the button.
    if (state.username === 'a' && state.password === 'a') {
      const newCommunicator = new ProxyCommunicator(state.username, state.password, state.url);
      setCommunicator(newCommunicator);
      localStorage.setItem('communicator', CommunicatorSerDe.serialize(newCommunicator));
      addUrl(state.url);

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

  const handleUrlChange = (newValue: string): void => {
    dispatch({
      type: 'setUrl',
      payload: newValue,
    });
  };

  // Output JSX here

  if (communicator) return <Redirect to="/" />;

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
            <Autocomplete
              id="combo-box-url"
              value={state.url}
              options={urls}
              freeSolo
              onChange={(_, newValue) => handleUrlChange(newValue === null ? '' : newValue)}
              renderInput={(params) => (
                <TextField
                  // eslint-disable-next-line react/jsx-props-no-spreading
                  {...params}
                  fullWidth
                  id="url"
                  label={t('Login.edit.url')}
                  placeholder="URL"
                  margin="normal"
                  onBlur={(event) => handleUrlChange(event.target.value)}
                />
              )}
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
              // TODO: This eliminates a warning that is sent to the console. It's ugly but if you don't
              // do this, the SPA will reset itself when handleLogin fails.
              event.preventDefault();
              handleLogin();
            }}
          >
            <Trans>Login.button.login</Trans>
          </Button>
        </CardActions>
      </Card>
    </form>
  );
};

export default Login;
