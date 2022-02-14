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
    return <Card>
                <Accordion.Toggle as={Card.Header} variant="link" eventKey={props.eventKey}>
                    <h3>{props.dateRange.year} <Badge variant="secondary">{props.dateRange.pictureCount}</Badge></h3>
                </Accordion.Toggle>
                <Accordion.Collapse eventKey={props.eventKey}>
                    <Card.Body>
                        <ListGroup variant="flush">
                        {props.dateRange.dateRangeList.map((dateRange) => (
                            <Link to={getPictureLink(dateRange.start, dateRange.end)}>
                                <ListGroup.Item>{GetFrenchMonth(dateRange.start)}&nbsp;<Badge variant="secondary">{dateRange.pictureCount}</Badge></ListGroup.Item>
                            </Link>
                        ))}
                        </ListGroup>
                    </Card.Body>
                </Accordion.Collapse>
            </Card>
}

export default PictureDateMenuElement;