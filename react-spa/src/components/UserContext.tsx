import React, { FC, Dispatch, ReactNode, createContext, useReducer } from 'react';
import { useHistory } from 'react-router-dom';

import UserState from '../lib/UserState';
import Communicator from '../lib/Communicator';
import ProxyCommunicator from '../lib/ProxyCommunicator';

export type Action = { type: 'logout' } | { type: 'authenticated'; payload: Communicator };

export interface UserStore {
  state: UserState;
  dispatch: Dispatch<Action>;
}

const defaultState = new UserState();

const defaultStore: UserStore = {
  state: defaultState,
  dispatch: () => defaultState,
};

const context = createContext(defaultStore);

interface Props {
  children?: ReactNode;
}

export const Provider: FC<Props> = ({ children }) => {
  const history = useHistory();

  const reducer = (state: UserState, action: Action): UserState => {
    switch (action.type) {
      case 'logout': {
        const { communicator } = state;
        if (!communicator) return state;
        localStorage.removeItem('state');
        communicator.logout();
        if (history) setImmediate(() => history.push('/'));
        return new UserState();
      }
      case 'authenticated': {
        const newState = new UserState();
        newState.communicator = action.payload;
        localStorage.setItem('state', JSON.stringify(newState.communicator.username));
        if (history) setImmediate(() => history.push('/'));
        return newState;
      }
      default:
        throw new Error(`Invalid type: ${action}`);
    }
  };

  // Retrieve state from local state
  let initialState = defaultState;

  {
    const fromStorage = localStorage.getItem('state');
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let parsed: any;

    if (fromStorage) {
      try {
        parsed = JSON.parse(fromStorage);
      } catch (error) {
        //
      }
    }

    if (parsed) {
      initialState = new UserState();
      try {
        initialState.communicator = new ProxyCommunicator(parsed, '');
      } catch (error) {
        //
      }
    }
  }

  const [state, dispatch] = useReducer(reducer, initialState);
  return <context.Provider value={{ state, dispatch }}>{children}</context.Provider>;
};

/**
 * @return The active UserStore based on the calling Element location
 */
// eslint-disable-next-line react-hooks/rules-of-hooks
const use = (): UserStore => React.useContext<UserStore>(context);

export default { Provider, use };
