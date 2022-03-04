import * as React from 'react';
import { Form } from 'react-bootstrap';

interface IPictureSizeSelectorProps {
    startSize: number;
    minSize: number;
    maxSize: number;
    onSizeChange: (newSize: number) => void;
}


const PictureSizeSelector : React.FunctionComponent<IPictureSizeSelectorProps> = (props) => {
    const [currentSize, setCurrentSize] = React.useState<number>(props.startSize);

    const onChange : React.ChangeEventHandler<HTMLInputElement> = (event) => {
        setCurrentSize(parseInt(event.target.value));
        props.onSizeChange(currentSize);
    };

    return <div>
        <Form.Range
            min={props.minSize}
            max={props.maxSize}
            step={20}
            value={currentSize}
            onChange={onChange} 
        />
    </div>
    
}

export default PictureSizeSelector;