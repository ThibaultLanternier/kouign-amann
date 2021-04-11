import { debug } from "console";
import { IPicture, IPictureInfo } from "./App";
import { PictureConverter, PictureInfoConverter, ReduceString, RefreshPictureList } from "./Tools"

test('PictureInfoConverter', () => {
    const date_string = "1972-03-01T20:00:03.000000Z";
    const expected_date = new Date(date_string);

    const picture_info : IPictureInfo = {
        creation_time : "1972-03-01T20:00:03.000000Z",
        thumbnail: "xxxx",
    }

    expect(PictureInfoConverter(picture_info).creation_time_date).toStrictEqual(expected_date)
});

test('PictureConverter', () => {
   const picture : IPicture = {
       hash: "xx",
       backup_required: true,
       info: {
            creation_time : "1972-03-01T20:00:03.000000Z",
            thumbnail: "xxxx",
        },
        file_list: [],
        backup_list: [],
   } 

   const convertedPicture = PictureConverter(picture);

   expect(convertedPicture.info.creation_time_date).toBeInstanceOf(Date);
   expect(convertedPicture.rank).toEqual(1);
});

test('ReduceString', () => {
    const testInput = "0123456789";
    const expectedOutput = "...6789";

    expect(ReduceString(testInput, 4)).toEqual(expectedOutput);
});

test('ReduceString short string', () => {
    const testInput = "0123456789";

    expect(ReduceString(testInput, 10)).toEqual(testInput);
});

test("RefreshPictureList", () => {
    const picture: IPicture = {
        hash: "aaaa",
        info: {
            creation_time: "1980-11-30",
            thumbnail: "xxx",
        },
        backup_required: false,
        file_list: [],
        backup_list: [],
        rank: 1,
    };

    const pictureList: IPicture[] = [
        picture,
        {...picture, hash: "bbbb"}
    ];

    const updatedPictureList: IPicture[] = [
        {...picture, backup_required: true}
    ];
    
    const refreshedList = RefreshPictureList(pictureList, updatedPictureList);
    
    expect(refreshedList[0].backup_required).toBeTruthy();
    expect(refreshedList[0].rank).toEqual(2);
    expect(refreshedList[1].backup_required).toBeFalsy();
    expect(refreshedList[1].rank).toEqual(1);
});