import * as React from 'react';
import Picture from './Picture';
import { IPicture } from './Interfaces';
import { Card, Alert, Spinner } from 'react-bootstrap';
import PictureInfoModal from './PictureInfoModal';
import { IPictureAPI } from './Services';
interface IPictureListProps {
    pictures: IPicture[];
    loading: boolean;
    pictureAPI: IPictureAPI;
}

const PictureList : React.FunctionComponent<IPictureListProps> = (props) => {
    const [activePictureInfo, setActivePictureInfo] = React.useState<IPicture|undefined>();

    const onShowInfo = (pictureInfo: IPicture) => {
        setActivePictureInfo(pictureInfo);
    }

    const unSelectActivePicture = () => {
        setActivePictureInfo(undefined);
    }

    const renderPictureInfo = () => {
        if(activePictureInfo !== undefined) {
            return <PictureInfoModal pictureInfo={activePictureInfo} onClose={unSelectActivePicture}></PictureInfoModal>    
        }
    }

    return <Card>
                <Card.Body>
                    {renderPictureInfo()}
                    <Alert 
                        variant={props.pictures.length > 0 ? "primary" : "warning"}
                    >
                        {props.pictures.length} pictures { props.loading && <Spinner size="sm" animation="border" />}
                    </Alert>
                    {props.pictures.map(picture => (
                        <Picture 
                            key={picture.hash + "-" + picture.rank}
                            picture={picture} 
                            onShowInfo={onShowInfo}
                            pictureAPI={props.pictureAPI}
                        ></Picture>
                    ))}
                </Card.Body>
            </Card>
}

export default PictureList