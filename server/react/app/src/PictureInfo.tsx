import * as React from 'react';
import { Modal } from 'react-bootstrap';
import { IPicture } from './App';
import PictureFileInfo from './PictureFileInfo';
import './PictureInfo.css';

export interface IPictureInfoProps {
    pictureInfo: IPicture;
    onClose: () => void;
}

const PictureInfo : React.FunctionComponent<IPictureInfoProps> = (props) => {
    return <Modal show={true} onHide={props.onClose}>
                <Modal.Header closeButton><h5>Info</h5></Modal.Header>
                <Modal.Body>
                    <p><b>Hash:</b>&nbsp;{props.pictureInfo.hash}</p>
                    <p><b>Created:</b>
                        &nbsp;{props.pictureInfo.info.creation_time_date?.toLocaleDateString()}
                        &nbsp;{props.pictureInfo.info.creation_time_date?.toLocaleTimeString()}
                    </p>
                    <p><b>Files:</b></p>
                    {props.pictureInfo.file_list.map(file => (
                        <PictureFileInfo {...file}></PictureFileInfo>
                    ))}
                    <p><b>Backup:</b></p>
                    <ul>
                    {props.pictureInfo.backup_list.map(backup => (
                        <li>{backup.crawler_id} - {backup.status}</li>
                    ))}
                    </ul>
                </Modal.Body>
            </Modal>
}

export default PictureInfo;