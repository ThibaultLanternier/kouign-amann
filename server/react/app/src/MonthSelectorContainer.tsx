import * as React from 'react';
import { PictureAPI } from './Services';
import { IDateRange } from './Interfaces';
import { groupDateRangeByYear } from './Tools';
import MonthSelector from './MonthSelector';
import { useParams } from 'react-router-dom';

const apiURL = process.env.REACT_APP_API_URL as string;

const pictureAPI = new PictureAPI(apiURL);

const MonthSelectorContainer : React.FunctionComponent = () => {
    const [dateRange, setDateRange] = React.useState<IDateRange[]>([]);

    const {start, end} = useParams();
    
    React.useEffect(() => {
        pictureAPI.retrieveDateRangeList().then((dateRange) => {
            setDateRange(dateRange);
        })
    }, []);

    React.useEffect(() => {
        if(start !== undefined && end !== undefined) {

        };
    }, [start, end]);

    return <MonthSelector 
        dateList={ groupDateRangeByYear(dateRange)} 
    />
};

export default MonthSelectorContainer;