
import './Custom-Bootstrap.scss';

import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter } from 'react-router-dom';
import AppFunction from './AppFunction';

ReactDOM.render(
  <BrowserRouter>
    <AppFunction />
  </BrowserRouter>,
  document.getElementById('root')
);
