import React, { createContext } from 'react';
import UserStore from '../lib/UserStore';

const userStore = new UserStore();
const UserStoreContext = createContext(userStore);

const UserStoreProvider: React.FC = (props) => (
  // eslint-disable-next-line react/destructuring-assignment
  <UserStoreContext.Provider value={userStore}>{props.children}</UserStoreContext.Provider>
);

const UserStoreConsumer = UserStoreContext.Consumer;

export { UserStore, UserStoreProvider, UserStoreConsumer };
