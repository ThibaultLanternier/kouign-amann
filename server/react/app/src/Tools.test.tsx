import { IDateRange, IPicture, IPictureInfo } from "./Model";
import { GetFrenchMonth, getPictureLink, GroupDateRangeByYear, PictureConverter, PictureInfoConverter, ReduceString, RefreshPictureList } from "./Tools"

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

test("GroupDateRangeByYear", () => {
    const dateRange1980 : IDateRange = {id:1, start: new Date("1980-11-10"), end: new Date("1980-11-10"), pictureCount: 1}
    const dateRange1980_1 : IDateRange = {id:1, start: new Date("1980-12-10"), end: new Date("1980-12-11"), pictureCount: 2}
    const dateRange1981 : IDateRange = {id:1, start: new Date("1981-11-10"), end: new Date("1981-11-10"), pictureCount: 1}

    const dateRangeList : IDateRange[] = [dateRange1980, dateRange1980_1, dateRange1981];

    const yearDateRangeList = GroupDateRangeByYear(dateRangeList);

    expect(yearDateRangeList).toEqual([
        {year:1980, pictureCount: 3, dateRangeList: [dateRange1980, dateRange1980_1]},
        {year:1981, pictureCount: 1, dateRangeList: [dateRange1981]},
    ])
});

test("GetFrenchMonth", () => {
    expect(GetFrenchMonth(new Date("1980-11-10"))).toEqual("Novembre");
});

test("getPictureLink", () => {
    expect(
        getPictureLink(new Date("1980-02-03"), new Date("1980-02-05"))
    ).toEqual("/pictures/1980-02-03T00:00:00.000Z/1980-02-05T00:00:00.000Z");
});