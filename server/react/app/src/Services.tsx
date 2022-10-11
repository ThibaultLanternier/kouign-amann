import { IPicture, IDateRange } from "./Interfaces";
import axios, { AxiosResponse } from 'axios';
import {PictureConverter} from './Tools';
export interface IPictureAPI {
    setBackup: (pictureHash: string, backup: boolean) => Promise<void>;
    planBackup: (pictureHash: string) => Promise<void>;
    getPictureInfo: (pictureHash: string) => Promise<IPicture>;
    setAndPlanBackup: (pictureHash: string, backup: boolean) => Promise<IPicture>;
    getPictureList: (startTime: Date, endTime: Date) => Promise<IPicture[]>;
}

export interface IGoogleAuthAPI {
    getAuthenticationLink: () => Promise<string>;
}
interface monthlyPictureCount {
    date: string;
    count: number;
    start_date: string;
    end_date: string;
}

export class GoogleAuthAPI implements IGoogleAuthAPI {
    private serverURL: string;

    constructor(serverURL: string) {
        this.serverURL = serverURL;
    }

    public getAuthenticationLink() : Promise<string> {
        return axios.get<string>(
            `${this.serverURL}/auth/google`
        ).then((response: AxiosResponse<string>) => {
            return response.data;
        })
    }
}
export class PictureAPI implements IPictureAPI {
    private serverURL: string;

    constructor(serverURL: string) {
        this.serverURL = serverURL;
    }

    public setBackup(pictureHash: string, backup: boolean): Promise<void> {
        if(backup) {
            return axios.post(
                `${this.serverURL}/backup/request/${pictureHash}`
            ).then((response) => {
                return;
            });
        } else {
            return axios.delete(
                `${this.serverURL}/backup/request/${pictureHash}`
            ).then((response) => {
                return;
            });
        }
    }

    public retrieveDateRangeList() : Promise<IDateRange[]> {
        return axios.get<monthlyPictureCount[]>(`${this.serverURL}/picture/count`).then((response) => {
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

            return dateRangeList;
        });
      }

    public planBackup(pictureHash: string) : Promise<void> {
        return axios.put(
            `${this.serverURL}/backup/plan/${pictureHash}`
        ).then(() => {
            return;
        });
    }

    public getPictureInfo(pictureHash: string) : Promise<IPicture> {
        return axios.get<IPicture>(
            `${this.serverURL}/picture/${pictureHash}`
        ).then((response: AxiosResponse<IPicture>) => {
            return response.data
        });
    }

    public setAndPlanBackup(pictureHash: string, backup: boolean) : Promise<IPicture> {
        return this.setBackup(pictureHash, backup).then(() => {
            return this.planBackup(pictureHash);
        }).then(() => {
            return this.getPictureInfo(pictureHash);
        })
    }

    public getRecentlyUpdatedPictures(timeFrame: number) : Promise<IPicture[]> {
        return axios.get<IPicture[]>(
            `${this.serverURL}/picture/updated/${timeFrame}`
        ).then((response: AxiosResponse<IPicture[]>) => {
            return response.data.map(PictureConverter);
        });
    }

    public getPictureList(startTime: Date, endTime: Date) : Promise<IPicture[]> {
        return axios.get<IPicture[]>(
            `${this.serverURL}/picture/list`,
            {
                params:{
                    start: startTime.toISOString(),
                    end: endTime.toISOString(),
                }
            })
        .then((response: AxiosResponse<IPicture[]>) => {
            return response.data.map(PictureConverter)
        });
    }
}
