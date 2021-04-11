import * as React from 'react';
import { Alert } from 'react-bootstrap';
import {IFile} from './App';
import {ReduceString} from './Tools';

const PictureFileInfo : React.FunctionComponent<IFile> = (props) => {
    return <Alert title={props.picture_path} variant="primary">{ReduceString(props.picture_path, 30)}</Alert>
}

export default PictureFileInfo;