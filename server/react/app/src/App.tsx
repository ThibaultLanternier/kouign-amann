import * as React from 'react';
import { Container } from 'react-bootstrap';
import { Route, Routes } from 'react-router-dom';
import PictureListContainer from './PictureListContainer';
import MonthSelectorContainer from './MonthSelectorContainer';

const App : React.FunctionComponent = () => {
    const [pictureSize, setPictureSize] = React.useState<number>(300);
    
    return <Container fluid>
      <MonthSelectorContainer
        onPictureSizeChange={setPictureSize}
      />
      <Routes>
        <Route path="/pictures/:start/:end" element={ <PictureListContainer pictureSize={pictureSize}/>}/>
      </Routes>
      <p>{process.env.NODE_ENV} - {process.env.REACT_APP_API_URL}</p>
    </Container>
};

export default App;