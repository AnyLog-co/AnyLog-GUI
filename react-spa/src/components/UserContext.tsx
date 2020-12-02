import React, { ReactNode, createContext, useContext } from 'react';
import UserStore from '../lib/UserStore';

const userStore = new UserStore();
const UserContext = createContext(userStore);

interface Props {
  value?: UserStore;
  children?: ReactNode;
}

export const UserContextProvider: React.FC<Props> = ({ value = userStore, children }) => (
  <UserContext.Provider value={value}>{children}</UserContext.Provider>
);

export const UserContextConsumer = UserContext.Consumer;

/**
 * @return The active UserStore based on the calling Element location
 */
// eslint-disable-next-line react-hooks/rules-of-hooks
export const useUserContext = (): UserStore => useContext(UserContext);

export default { UserContextProvider, UserContextConsumer, useUserContext };
