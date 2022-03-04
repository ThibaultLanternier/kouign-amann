import * as React from 'react';
import { Badge, Card, Dropdown, DropdownButton, Row, Col } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { IYearDateRange } from './Interfaces';
import { IMonthSelectorContainerProps } from './MonthSelectorContainer';
import PictureSizeSelector from './PictureSizeSelector';
import { getFrenchMonth, buildDateRangeLink } from './Tools';

interface IMonthSelectorProps extends IMonthSelectorContainerProps{
    dateList : IYearDateRange[];
}

const MonthSelector : React.FunctionComponent<IMonthSelectorProps> = (props) => {
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
            <Row>
                <Col>
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
                        title={activeMonth !== undefined ? getFrenchMonth(activeMonth) : "Mois"}
                        onSelect={monthSelect}
                    >
                        {activeYear?.dateRangeList.map((dateRange, index) => (
                            <Dropdown.Item eventKey={index} as={Link} to={buildDateRangeLink(dateRange.start, dateRange.end)}>
                                {getFrenchMonth(dateRange.start)}&nbsp;<Badge bg="secondary">{dateRange.pictureCount}</Badge>
                            </Dropdown.Item>
                        ))}
                    </DropdownButton>
                </Col>
                <Col>
                    <PictureSizeSelector
                        minSize={40}
                        maxSize={800}
                        startSize={200}
                        onSizeChange={props.onPictureSizeChange}    
                    />
                </Col>
            </Row>
        </Card.Body>    
    </Card>
};

export default MonthSelector;