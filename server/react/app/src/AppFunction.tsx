import './App.css'

import * as React from 'react';
import { Col, Container, Row } from 'react-bootstrap';
import { Route, Routes } from 'react-router-dom';
import PictureContainer from './PictureContainer';
import PictureDateRange from './PIctureDateRange';

const AppFunction : React.FunctionComponent = () => {
    return <Container fluid>
    <Row>
      <Col>
        <PictureDateRange />
      </Col>
      <Col>
        <Routes>
          <Route path="/pictures/:start/:end" element={ <PictureContainer/>}/>
        </Routes>
      </Col>
    </Row>
    <p>{process.env.NODE_ENV} - {process.env.REACT_APP_API_URL}</p>
  </Container>
};

export default AppFunction;