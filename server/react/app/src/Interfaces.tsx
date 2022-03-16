export interface IDateRange {
    start: Date;
    end: Date;
    pictureCount: number;
    id: number;
  }
  
  export interface IYearDateRange {
    year: number;
    pictureCount: number;
    dateRangeList: IDateRange[];
  }

  export interface IPictureInfo {
    creation_time: string;
    thumbnail: string;
    creation_time_date?: Date
    orientation: string;
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