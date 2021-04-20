import './Picture.css';
import './Picture.css';

import * as React from 'react';
import {Image} from 'react-bootstrap';
import {IBackup, IPicture} from './App'
import { Button } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faClock, faCloudUploadAlt } from '@fortawesome/free-solid-svg-icons'
import { IPictureAPI } from './Services';
export interface IPictureProps {
    picture: IPicture;
    onShowInfo: (picture: IPicture) => void;
    pictureAPI: IPictureAPI;
}

const Picture : React.FunctionComponent<IPictureProps> = (props) => {
    const [pictureData, setPictureData] = React.useState<IPicture>(props.picture);
    const [isUpdating, setIsUpdating] = React.useState<boolean>(false);

    const onHandleClick = (event: React.MouseEvent) => {
      if(!isUpdating){
        setIsUpdating(true);
        props.pictureAPI.setAndPlanBackup(pictureData.hash, !pictureData.backup_required).then((newPictureData) => {
          setIsUpdating(false);
          setPictureData(newPictureData);
        }).catch((error) => {
          setIsUpdating(false);
          alert("Not OK");
        });
      }
    }
    
    const onHandleMouseOver = (event: React.MouseEvent) => {
        props.onShowInfo(pictureData);
    }

    const getIconColor = (backupList: IBackup[]) => {
      const totalBackupCount = backupList.length;

      const NOT_PLANNED = "text-muted";
      const ON_GOING = "text-warning";
      const DONE = "text-success";
      const ERROR = "text-danger";

      if(totalBackupCount === 0){
        return NOT_PLANNED;
      } else {
        const completedBackupCount = backupList.filter(backup => backup.status === "DONE");

        if(completedBackupCount.length === totalBackupCount){
          return DONE;
        } else {
          const errorBackupCount = backupList.filter(backup => backup.status === "ERROR");

          if(errorBackupCount.length > 0){
            return ERROR;
          }

          return ON_GOING;
        }
      }
    }

    const renderCloudIcon = () => {
        if(isUpdating) {
          return <FontAwesomeIcon className={"text-muted icon"} size="2x" icon={faClock}></FontAwesomeIcon>
        }
        if(pictureData.backup_required) {
            return <FontAwesomeIcon className={[getIconColor(pictureData.backup_list), "icon"].join(' ')} size="2x" icon={faCloudUploadAlt} /> 
        }
    }

    return <div className="picture-container mr-1 mb-1" title={pictureData.hash}>
            <Image 
                title={pictureData.info.creation_time} alt={pictureData.hash} src={'data:image/jpeg;base64,' +  pictureData.info.thumbnail} 
            />
            <div className="overlay">
              <Button onClick={onHandleMouseOver} className="top-right" size="sm">?</Button>
              <div className="clickable" onClick={onHandleClick}></div>
              {renderCloudIcon()}
            </div>
        </div>

}

export default Picture