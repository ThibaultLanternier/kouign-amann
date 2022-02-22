import * as React from 'react';
import { Badge, Card, Dropdown, DropdownButton } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { IYearDateRange } from './Model';
import { GetFrenchMonth, getPictureLink } from './Tools';

interface IPictureSelectorProps {
    dateList : IYearDateRange[];
}

const PictureSelector : React.FunctionComponent<IPictureSelectorProps> = (props) => {
    const [activeYear, setActiveYear] = React.useState<IYearDateRange>();
    const [activeMonth, setActiveMonth] = React.useState<Date>();

    const yearSelect : (eventKey: string | null, e: React.SyntheticEvent<unknown>) => void = (eventKey, e) => {
        if(eventKey !== null) {
            const eventKeyNum : number = parseInt(eventKey);

            if(props.dateList[eventKeyNum] !== undefined) {
                setActiveYear(props.dateList[eventKeyNum]);
                setActiveMonth(undefined);
            };
        };
    };

    const monthSelect : (eventKey: string | null, e: React.SyntheticEvent<unknown>) => void = (eventKey, e) => {
        if(eventKey !== null) {
            const eventKeyNum : number = parseInt(eventKey);

            if(activeYear !== undefined) {
                if(activeYear.dateRangeList[eventKeyNum] !== undefined) {
                    setActiveMonth(activeYear.dateRangeList[eventKeyNum].start);
                }
            }
        }    
    };

    return <Card className="mb-2 sticky-top">
        <Card.Body>
            <DropdownButton 
                className="d-inline-block me-2" 
                title={activeYear !== undefined ? activeYear?.year : "Année"} 
                onSelect={yearSelect}
            >
                {props.dateList.map((date, index) => (
                    <Dropdown.Item eventKey={index}>{date.year} <Badge bg="secondary">{date.pictureCount}</Badge></Dropdown.Item>
                ))}
            </DropdownButton>
            <DropdownButton 
                className="d-inline-block" 
                title={activeMonth !== undefined ? GetFrenchMonth(activeMonth) : "Mois"}
                onSelect={monthSelect}
            >
                {activeYear?.dateRangeList.map((dateRange, index) => (
                    <Dropdown.Item eventKey={index} as={Link} to={getPictureLink(dateRange.start, dateRange.end)}>
                        {GetFrenchMonth(dateRange.start)}&nbsp;<Badge bg="secondary">{dateRange.pictureCount}</Badge>
                    </Dropdown.Item>
                ))}
            </DropdownButton>
        </Card.Body>    
    </Card>
};

export default PictureSelector;