import './App.css'

import * as React from 'react';
import { Container } from 'react-bootstrap';
import { Route, Routes } from 'react-router-dom';
import PictureContainer from './PictureContainer';
import PictureDateRange from './PIctureDateRange';

const AppFunction : React.FunctionComponent = () => {
    return <Container fluid>
      <PictureDateRange/>
      <Routes>
        <Route path="/pictures/:start/:end" element={ <PictureContainer/>}/>
      </Routes>
      <p>{process.env.NODE_ENV} - {process.env.REACT_APP_API_URL}</p>
    </Container>
};

export default AppFunction;