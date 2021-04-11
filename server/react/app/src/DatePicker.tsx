import * as React from 'react';
import Form from 'react-bootstrap/Form';

interface datePickerProps {
    onDateChange : (newDate: Date) => void,
    currentDate: Date,
    title: string,
}

interface datePickerState {
    dateValue: string,
    isoDate: string,
}

class DatePicker extends React.Component<datePickerProps, datePickerState> {
    constructor(props: datePickerProps) {
        super(props);

        this.state = {
            dateValue: props.currentDate.toISOString(),
            isoDate: props.currentDate.toISOString(),
        }
    }

    onDateValueChange = (e: React.ChangeEvent<HTMLInputElement>) : void => {
        this.setState({
            dateValue: e.currentTarget.value
        })
        
        try {
            let newDate: Date = new Date(e.currentTarget.value);
            let isoNewDate = newDate.toISOString();
            this.setState({
                isoDate: isoNewDate,
            })
            this.props.onDateChange(newDate);
        } catch(error) {
            console.error(error)
            this.setState({
                isoDate: "Not OK"
            })
        }
    }

    componentDidUpdate(prevProps: datePickerProps, prevState: datePickerState) {
        console.log("Update", this.props.title, this.props.currentDate) 
        
        if(prevProps.currentDate !== this.props.currentDate){
            if(this.props.currentDate !== undefined){
                this.setState({
                    dateValue: this.props.currentDate.toISOString(),
                    isoDate: this.props.currentDate.toISOString(),
                })
            }
        }
    }

    public render() {
        return [
            <Form.Control
                aria-label="my-date-picker" 
                value={this.state.dateValue} 
                type="text" 
                placeholder="2020-01-01T12:00:00"
                onChange={this.onDateValueChange}
                className="mr-2"
            />
        ]      
    }
}

export default DatePicker