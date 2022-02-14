import * as React from 'react';
import PictureDateMenu from './PictureDateMenu';
import { PictureAPI } from './Services';
import { IDateRange } from './Model';
import { GroupDateRangeByYear } from './Tools';

const apiURL = process.env.REACT_APP_API_URL as string;

const pictureAPI = new PictureAPI(apiURL);

const PictureDateRange : React.FunctionComponent = () => {
    const [dateRange, setDateRange] = React.useState<IDateRange[]>([]);
    
    React.useEffect(() => {
        pictureAPI.retrieveDateRangeList().then((dateRange) => {
            setDateRange(dateRange);
        })
    }, []);

    return <PictureDateMenu 
        dateList={ GroupDateRangeByYear(dateRange)} 
    />
};

export default PictureDateRange;