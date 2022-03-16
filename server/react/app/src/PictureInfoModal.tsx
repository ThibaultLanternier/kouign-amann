import * as React from 'react';
import { Image, Modal } from 'react-bootstrap';
import { IPicture } from './Interfaces';
import FileInfo from './FileInfo';
import './PictureInfoModal.css';

export interface IPictureInfoProps {
    pictureInfo: IPicture;
    onClose: () => void;
}

const PictureInfoModal : React.FunctionComponent<IPictureInfoProps> = (props) => {
    return <Modal show={true} onHide={props.onClose} size="xl">
                <Modal.Header closeButton><h5>Info</h5></Modal.Header>
                <Modal.Body>
                    <p><b>Hash:</b>&nbsp;{props.pictureInfo.hash}</p>
                    <Image
                        title={props.pictureInfo.info.creation_time}  
                        alt={props.pictureInfo.hash} 
                        src={'data:image/jpeg;base64,' +  props.pictureInfo.info.thumbnail}
                        style={{maxWidth: "100%"}}
                    />
                    <p><b>Created:</b>
                        &nbsp;{props.pictureInfo.info.creation_time_date?.toLocaleDateString()}
                        &nbsp;{props.pictureInfo.info.creation_time_date?.toLocaleTimeString()}
                    </p>
                    <p><b>Files:</b></p>
                    {props.pictureInfo.file_list.map(file => (
                        <FileInfo {...file}></FileInfo>
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

export default PictureInfoModal;