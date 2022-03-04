import * as React from 'react';
import { useParams } from 'react-router-dom';
import { IPicture } from './Interfaces';
import PictureList from './PictureList';
import { PictureAPI } from './Services';
import { refreshPictureList } from './Tools';

interface IPictureListContainerProps {
    pictureSize: number;
}

const apiURL = process.env.REACT_APP_API_URL as string;
const pictureAPI = new PictureAPI(apiURL)

const PictureListContainer : React.FunctionComponent<IPictureListContainerProps> = (props) => {
    const {start, end} = useParams();

    const [pictureLoading, setPictureLoading] = React.useState<boolean>(true);
    const [pictureList, setPictureList] = React.useState<IPicture[]>([]);

    React.useEffect(() => {
        if(start !== undefined && end !== undefined){
            setPictureLoading(true);
            
            const startDate = new Date(start);
            const endDate = new Date(end);
    
            pictureAPI.getPictureList(startDate, endDate).then((pictureList) => {
                setPictureLoading(false);
                setPictureList(pictureList);
            });
        }
    }, [start,end]);
    
    React.useEffect(() => {
        console.log(props.pictureSize);
    }, [props])

    React.useEffect(() => {
        const interval = setInterval(() => {
            console.log("Refreshing picture list");
            pictureAPI.getRecentlyUpdatedPictures(30).then((recentlyUpdatedPictureList => {
                const updatedPictureList = refreshPictureList(
                  pictureList,
                  recentlyUpdatedPictureList
                );
                setPictureList(updatedPictureList);
              }));        
        }, 10000);
        return () => clearInterval(interval);
    }, [pictureList]);

    return <div>
        <PictureList
            pictures={pictureList}
            pictureAPI={pictureAPI}
            loading={pictureLoading} 
            pictureSize={props.pictureSize}
        />
    </div>
}

export default PictureListContainer;