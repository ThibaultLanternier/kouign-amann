import * as React from 'react';
import { IYearDateRange } from './Model';
import { Accordion } from 'react-bootstrap';
import PictureDateMenuElement from './PictureDateMenuElement';

interface IPictureDateMenuProps {
    dateList : IYearDateRange[];
}

const PictureDateMenu : React.FunctionComponent<IPictureDateMenuProps> = (props) => {
    return <Accordion>
        {props.dateList.map((date, index) => (
            <PictureDateMenuElement key={index} dateRange={date} eventKey={index.toString()}/>
        ))}
    </Accordion>
}

export default PictureDateMenu;