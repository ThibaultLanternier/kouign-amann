import { IPicture } from "./App";
import axios, { AxiosResponse } from 'axios';
import {PictureConverter} from './Tools';
export interface IPictureAPI {
    setBackup: (pictureHash: string, backup: boolean) => Promise<void>;
    planBackup: (pictureHash: string) => Promise<void>;
    getPictureInfo: (pictureHash: string) => Promise<IPicture>;
    setAndPlanBackup: (pictureHash: string, backup: boolean) => Promise<IPicture>;
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