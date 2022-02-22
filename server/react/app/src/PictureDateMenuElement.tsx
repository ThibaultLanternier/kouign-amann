import * as React from 'react';
import { Accordion, Badge, Card, ListGroup } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { IYearDateRange } from './Model';
import { GetFrenchMonth, getPictureLink } from './Tools';

interface IPictureDateMenuElementProps {
    dateRange : IYearDateRange;
    eventKey: string;
}

const PictureDateMenuElement : React.FunctionComponent<IPictureDateMenuElementProps> = (props) => {
    return <Accordion.Item eventKey={props.eventKey}>
                <Accordion.Header>
                    <h5>{props.dateRange.year} <Badge bg="secondary">{props.dateRange.pictureCount}</Badge></h5>
                </Accordion.Header>
                <Accordion.Body>
                    <ListGroup variant="flush">
                    {props.dateRange.dateRangeList.map((dateRange) => (
                        <Link to={getPictureLink(dateRange.start, dateRange.end)}>
                            <ListGroup.Item>{GetFrenchMonth(dateRange.start)}&nbsp;<Badge bg="secondary">{dateRange.pictureCount}</Badge></ListGroup.Item>
                        </Link>
                    ))}
                    </ListGroup>
                </Accordion.Body>
            </Accordion.Item>
}

export default PictureDateMenuElement;