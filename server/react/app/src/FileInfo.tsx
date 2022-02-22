import * as React from 'react';
import { Alert } from 'react-bootstrap';
import {IFile} from './Interfaces';
import {shortenString} from './Tools';

const FileInfo : React.FunctionComponent<IFile> = (props) => {
    return <Alert title={props.picture_path} variant="primary">{shortenString(props.picture_path, 30)}</Alert>
}

export default FileInfo;