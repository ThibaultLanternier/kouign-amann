import axios from "axios";
import { PictureAPI } from "./Services";

jest.mock('axios');

const mockAxios = axios as jest.Mocked<typeof axios>;

/**
 * Note : in order to debug test
 * 
 * yarn test:debug
 * 
 * then open chrome://inspect in Chrome
 * 
 * put "debugger;" inside the code to set a breakpoint
 */

describe("PictureAPI", () => {
    const result = {data: "data"};
    const testAPI = new PictureAPI("SERVER");

    const fakePictureList = [
        {
            "hash": "9bf6925b2702652e",
            "info": {
                "creation_time": "1970-01-01T00:00:00.000000Z",
                "thumbnail": "xxxx",
            },
            "backup_required": true,
            "file_list": [
                {
                    "crawler_id": "thibault-laptop-new-6776ZJHGbGGSHG",
                    "resolution": [
                        1523,
                        2267
                    ],
                    "picture_path": "/home/thibault/Images/2007/06/02/000036.JPG",
                    "last_seen": "2021-01-01T17:00:06.153000Z"
                }
            ],
            "backup_list": [
                {
                    "crawler_id": "thibault-laptop-new-6776ZJHGbGGSHG",
                    "storage_id": "xxxx",
                    "file_path": "/home/thibault/Images/2007/06/02/000036.JPG",
                    "status": "PENDING",
                    "creation_time": "2021-03-31T20:06:09.569000Z"
                }
            ]
        }
    ]

    beforeEach(() => {
        mockAxios.get.mockResolvedValue(result);
        mockAxios.post.mockResolvedValue(result);
        mockAxios.put.mockResolvedValue(result);
        mockAxios.delete.mockResolvedValue(result);
    });

    afterEach(() => {
        mockAxios.get.mockReset();
        mockAxios.post.mockReset();
        mockAxios.put.mockReset();
        mockAxios.delete.mockReset();
    });

    test("setBackup true", () => {
        return testAPI.setBackup("hash", true).then((response) => {
            expect(response).toBeUndefined()
            expect(mockAxios.post).toHaveBeenCalledWith("SERVER/backup/request/hash");
        });
    });

    test("setBackup false", () => {
        return testAPI.setBackup("hash", false).then((response) => {
            expect(response).toBeUndefined()
            expect(mockAxios.delete).toHaveBeenCalledWith("SERVER/backup/request/hash");
        });
    });

    test("setBackup error", () => {
        return testAPI.setBackup("hash", false).catch((response) => {
            expect(response).toBeUndefined()
            expect(mockAxios.delete).toHaveBeenCalledWith("SERVER/backup/request/hash");
        });
    });

    test("planBackup ok", () => {
        return testAPI.planBackup("hash").then((response) => {
            expect(response).toBeUndefined()
            expect(mockAxios.put).toHaveBeenCalledWith("SERVER/backup/plan/hash");
        });
    });

    test("getPictureInfo ok", () => {
        return testAPI.getPictureInfo("hash").then((response) => {
            expect(response).toEqual("data");
            expect(mockAxios.get).toHaveBeenCalledWith("SERVER/picture/hash");
        });
    });

    test("getRecentlyUpdatedPictures", () => {
        mockAxios.get.mockResolvedValue({"data":fakePictureList});

        return testAPI.getRecentlyUpdatedPictures(60).then((response) => {
            expect(response[0].info.creation_time_date).toEqual(new Date("1970-01-01T00:00:00.000000Z"));
            expect(mockAxios.get).toHaveBeenCalledWith("SERVER/picture/updated/60")
        });
    });

    test("getPictureList", () => {
        mockAxios.get.mockResolvedValue({"data":fakePictureList});
        
        return testAPI.getPictureList(
            new Date("2020-11-01"), 
            new Date("2020-12-01")
        ).then((response) => {
            expect(response[0].info.creation_time_date).toEqual(new Date("1970-01-01T00:00:00.000000Z"));
            expect(response[0].backup_list[0].creation_time).toEqual("2021-03-31T20:06:09.569000Z");
            expect(mockAxios.get).toHaveBeenCalledWith(
                "SERVER/picture/list", 
                {"params": {"end": "2020-12-01T00:00:00.000Z", "start": "2020-11-01T00:00:00.000Z"}}
            );
        });
    });
});