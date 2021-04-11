import * as React from 'react';
import { Navbar, Nav, Form } from 'react-bootstrap';
import { IDateRange } from './App';
import DatePicker from './DatePicker';

interface pictureSelectorState {
    startTime: Date;
    endTime: Date;
}

interface pictureSelectorProps {
    onRangeChange: (startTime: Date, endTime: Date) => void
    dateRangeList: IDateRange[];
}

interface monthlyPictureCount {
    date: string;
    count: number;
}

const dateFormat = (input: Date) : string => {
    const month = ("0" + (input.getMonth() + 1)).slice(-2)
    const day = ("0" + input.getDate()).slice(-2)

    return `${input.getFullYear()}-${month}-${day}`;
}

class PictureSelector extends React.Component<pictureSelectorProps, pictureSelectorState> {
    constructor(props: pictureSelectorProps) {
        super(props)

        if(props.dateRangeList.length > 0) {
            const startTime = this.props.dateRangeList[0].start; 
            const endTime = this.props.dateRangeList[0].end;

            this.state = {
                startTime: startTime,
                endTime: endTime,
            }

            this.props.onRangeChange(startTime, endTime);    
        } else {
            this.state = {
                startTime: new Date(),
                endTime: new Date(),
            }
        }
    }

    onStartTimeChange = (e: Date) : void => {
        this.setState({
            startTime: e
        });
        this.props.onRangeChange(this.state.startTime, this.state.endTime);
    }

    onEndTimeChange = (e: Date) : void => {
        this.setState({
            endTime: e
        });
        this.props.onRangeChange(this.state.startTime, this.state.endTime);
    }

    onMonthSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) : void => {
        const dateRangeId = Number(e.currentTarget.value)
        console.log(dateRangeId)

        for (const dateRange of this.props.dateRangeList) {
            if (dateRange.id === dateRangeId) {
                this.setState({
                    startTime: dateRange.start,
                    endTime: dateRange.end,
                })
                console.log("Date range changed", dateRange)
                this.props.onRangeChange(
                    dateRange.start,
                    dateRange.end,
                )
            }
        }
    }

    componentDidUpdate(prevPros: pictureSelectorProps, prevState: pictureSelectorState) {
        if(this.props.dateRangeList !== prevPros.dateRangeList) {
            console.log("Date range received", this.props.dateRangeList)
            if (this.props.dateRangeList.length > 0) {
                const startTime = this.props.dateRangeList[0].start;
                const endTime = this.props.dateRangeList[0].end;

                this.setState({
                    startTime: startTime,
                    endTime: endTime,
                });

                this.props.onRangeChange(startTime, endTime);
            }
        }
    }

    public render() {
        return  <Navbar bg="dark" variant="dark" fixed="top">
                    <Navbar.Brand href="#home">Contact</Navbar.Brand>
                    <Nav>
                        <Form inline>
                            <Form.Control as="select" onChange={this.onMonthSelectChange} className="mr-2">
                                {this.props.dateRangeList.map(dateRange => (
                                    <option key={dateRange.id} value={dateRange.id} >{dateFormat(dateRange.start)} to {dateFormat(dateRange.end)} ({dateRange.pictureCount})</option>
                                    ))}
                            </Form.Control>
                            { this.props.dateRangeList.length > 0 &&
                                <DatePicker title="Start time" onDateChange={this.onStartTimeChange} currentDate={this.state.startTime}></DatePicker>
                            }
                            {  this.props.dateRangeList.length > 0 &&
                                <DatePicker title="End time" onDateChange={this.onEndTimeChange} currentDate={this.state.endTime}></DatePicker>
                            }
                        </Form>
                    </Nav>
                </Navbar>
    }
}

export default PictureSelector