import React from 'react';
import { Link } from 'react-router-dom';

const Home: React.FC = () => (
  <ul>
    <li>
      <Link to="/queryExample">Query Example</Link>
    </li>
    <li>
      <Link to="/network/nodes">Network Nodes</Link>
    </li>
  </ul>
);

export default Home;
