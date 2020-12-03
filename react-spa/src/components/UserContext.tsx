import React, { FC, Dispatch, ReactNode, createContext, useReducer } from 'react';
import { useHistory } from 'react-router-dom';

import UserState from '../lib/UserState';
import Communicator from '../lib/Communicator';

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
        state.logout();
        if (history) setTimeout(() => history.push('/'), 500);
        return new UserState();
      }
      case 'authenticated': {
        const newState = new UserState();
        newState.communicator = action.payload;
        if (history) setTimeout(() => history.push('/'), 500);
        return newState;
      }
      default:
        throw new Error(`Invalid type: ${action}`);
    }
  };

  const [state, dispatch] = useReducer(reducer, defaultState);
  return <context.Provider value={{ state, dispatch }}>{children}</context.Provider>;
};

/**
 * @return The active UserStore based on the calling Element location
 */
// eslint-disable-next-line react-hooks/rules-of-hooks
const use = (): UserStore => React.useContext<UserStore>(context);

export default { Provider, use };
