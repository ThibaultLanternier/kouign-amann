import './App.css';

import React from 'react';
import PictureSelector from './PictureSelector';
import axios from 'axios';
import { Container } from 'react-bootstrap';
import { PictureConverter, RefreshPictureList } from './Tools';
import { PictureAPI } from './Services';
import PictureList from './PictureList';
import { setInterval } from 'timers';

interface IAppState {
  pictureList: IPicture[];
  dateRangeList: IDateRange[];
  loadingPictures: boolean;
  activePictureInfo?: IPicture;
}

export interface IPictureInfo {
  creation_time: string;
  thumbnail: string;
  creation_time_date?: Date
}

export interface IFile {
  crawler_id: string;
  resolution: [number, number]
  picture_path: string;
  last_seen: string;

}

export interface IBackup {
  crawler_id: string;
  storage_id: string;
  file_path: string;
  status: string;
  creation_time: string;
}

export interface IPicture {
  hash: string;
  rank?: number;
  info: IPictureInfo;
  backup_required: boolean;
  file_list: IFile[]
  backup_list: IBackup[]
}

export interface IDateRange {
  start: Date;
  end: Date;
  pictureCount: number;
  id: number;
}

interface monthlyPictureCount {
  date: string;
  count: number;
  start_date: string;
  end_date: string;
}

const pictureAPI = new PictureAPI("http://localhost:5000")
class App extends React.Component<{}, IAppState> {
  public constructor(props: {}) {
      super(props);

      this.state = {
          pictureList: [],
          dateRangeList: [],
          loadingPictures: false,
      }
  }

  componentDidMount() {
    console.log("App has mounted");
    this.retrieveDateRangeList();

    setInterval(this.refreshPictureList, 10000);
  }

  onRangeChange = (start: Date, end: Date): void => {
    console.log("App received onRangeChange", start, end);
    this.updatePictureList(start, end);
  }

  retrieveDateRangeList = () => {
    console.log("Retrieving list of available date ranges")
    axios.get<monthlyPictureCount[]>("http://localhost:5000/picture/count").then((response) => {
        const dateRangeList: IDateRange[] = response.data.map((value, index) => {
            const startDate = new Date(value.start_date);
            const endDate = new Date(value.end_date);
            
            return {
                start: startDate,
                end: endDate,
                pictureCount: value.count,
                id: index,
            };
        })

        this.setState({
            dateRangeList: dateRangeList,
        })
    });
  }

  updatePictureList = (startTime: Date, endTime: Date) => {
    console.log("Retrieving pictures", startTime, endTime)
    this.setState({loadingPictures: true});
    
    axios.get<IPicture[]>(
        "http://localhost:5000/picture/list",
        {
            params:{
                start: startTime.toISOString(),
                end: endTime.toISOString(),
            }    
        })
    .then((response) => {
        console.log("Response OK", response)
        this.setState({
            pictureList: response.data.map(PictureConverter),
            loadingPictures: false,
        })
    });
  }

  refreshPictureList = () => {
    console.log("Retrieving recently updated pictures");

    pictureAPI.getRecentlyUpdatedPictures(30).then((recentlyUpdatedPictureList => {
      const updatedPictureList = RefreshPictureList(
        this.state.pictureList,
        recentlyUpdatedPictureList
      )
      console.log(`${recentlyUpdatedPictureList.length} pictures have been updated in the last 30 s.`)
      this.setState({
        pictureList: [...updatedPictureList]
      })  
    }));
  }

  public render() {
    return <Container fluid>
      <PictureSelector onRangeChange={this.onRangeChange} dateRangeList={this.state.dateRangeList}></PictureSelector>
      <PictureList 
        pictures={this.state.pictureList} 
        loading={this.state.loadingPictures}
        pictureAPI={pictureAPI}
      />
    </Container>
  }
}

export default App;
